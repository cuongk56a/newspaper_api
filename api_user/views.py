from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from .serializers import UserSerializer, UserShortWithEmailSerializer
from .service import UserService
from api_auth.permission import AdminPermission
from api_user.models import User
from base.views import BaseViewSet
from itertools import groupby

class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    permission_map = {
        "retrieve": [IsAuthenticated],
        "list": [AdminPermission],
        "change_password": [IsAuthenticated],
        "update_avatar": [IsAuthenticated],
    }


    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def list(self, request, *args, **kwargs):
        try:
            profiles = self.queryset.order_by('role')
            obj_users = []
            res_data = dict()
            for role, profile in groupby(profiles, lambda x: x.role):
                obj_users.append((role, [i for i in profile]))
            for user in obj_users:
                res_data.update({user[0]: self.serializer_class(user[1], many=True).data})
            return Response(res_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            user = get_object_or_404(User, pk=pk)
            user_serializes = UserShortWithEmailSerializer(user)
            return Response(data=user_serializes.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserShortWithEmailSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=False, url_path="change-password", serializer_class=UserSerializer)
    def change_password(self, request, *args, **kwargs):
        try: 
            account = request.user
            if account:
                if check_password(request.data["old_password"], account.password):
                    account.password = make_password(request.data["new_password"])
                    account.save()
                    return Response({'success': True, 'message': 'Changed password successfully!'}, status=status.HTTP_200_OK)
            return Response({"details": "Incorrect username! Change password unsuccessfully."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=['patch'], detail=False, url_path="update_avatar", serializer_class=UserSerializer)
    def update_avatar(self, request, *args, **kwargs):
        account = request.user
        instance = User.objects.filter(account=account).first()
        avatar = request.FILES.get('avatar')
        avatar_link = UserService.upload_avatar(avatar)
        request.data['avatar'] = avatar_link
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Your changes have been saved.', 'avatar_link':avatar_link}, status=status.HTTP_200_OK)