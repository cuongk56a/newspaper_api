from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework_simplejwt.tokens import RefreshToken

from api_user.serializers import UserSerializer
from .serializers import RegisterSerializer
from api_user.models import Account

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(method='POST', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'full_name': openapi.Schema(type=openapi.TYPE_STRING, default='User'),
        'phone': openapi.Schema(type=openapi.TYPE_STRING, default='0000000000'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, default='user@gmail.com'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, default='', format='password'),
    })
 )

@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def register_user(request):
    data = request.data
    serializer = RegisterSerializer(data=data)
    try:
        if serializer.is_valid(raise_exception=True):
            res_data = serializer.save()
            return Response(UserSerializer(res_data).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='POST', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Type your email', default='user@gmail.com'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Type your password', default='123456'),
    })
 )
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def login(request):
    password = request.data.get("password")
    email = request.data.get("email")
    try:
        account = Account.objects.filter(Q(email=email))
        if account.exists():
            account = account.first()
            if account.check_password(password):
                account.last_login = timezone.now()
                account.save()
                token = RefreshToken.for_user(account)
                return Response({
                    'user_id': account.user.id,
                    'email': email,
                    'full_name': account.user.full_name,
                    'avatar': account.user.avatar,
                    'address': account.user.address,
                    'phone': account.user.phone,
                    'birthday': account.user.birthday,
                    'access_token': str(token.access_token),
                    'refresh_token': str(token)
                })
        return Response( {"error": "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='POST', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Type refresh_token', default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1MjE3MzY5LCJpYXQiOjE3MjUyMTU1NjksImp0aSI6IjhjNTZhNDdmOGE3ZjQ5OWQ5N2MyZDk4NWVlZDQ3ZTY5IiwidXNlcl9pZCI6ImEwZDMyMTk2LTAyOGYtNGIyNy1hNTM1LWNjNjFhYjhjOGJkZSJ9.ujoeECpM1AI6Xg7UHnXH43nNXuRnY2Ti1Cig_PjtWjk'),
    })
 )    
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def token_refresh(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        token =  RefreshToken(refresh_token)

        return Response({
            'access_token': str(token.access_token),
            'refresh_token': str(token)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)