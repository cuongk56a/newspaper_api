from django.db.models import Q, Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from api_auth.permission import AdminPermission
from .models import Category, Source, Post
from .serializers import CategorySerializer, SourceSerializer, PostShortSerializer, PostSerializer,PostLikeSerializer
from .service import PostService
from .serivces import CrawlService
from base.views import BaseViewSet

class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    permission_map = {
      "Create": [AdminPermission]
    }

    def list(self, request, *args, **kwargs):
        params = request.query_params
        search_query = params.get("q", "")
        res_data = Category.objects.filter(Q(title__icontains=search_query))
        page = self.paginate_queryset(res_data)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(res_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SourceViewSet(BaseViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        params = request.query_params
        search_query = params.get("q", "")
        res_data = Source.objects.filter(Q(title__icontains=search_query))
        page = self.paginate_queryset(res_data)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(res_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostViewSet(BaseViewSet):
    queryset = Post.objects.all()
    permission_class = [AllowAny]
    permission_classes = [AllowAny]
    serializer_class = PostSerializer
    permission_map = {
        "create": [AdminPermission],
        "update": [AdminPermission],
        "get_post_management": [AdminPermission],
        "update_list_status_post": [AdminPermission],
    }
    serializer_map = {
        "list": PostShortSerializer,
    }

    def retrieve(self, request, *args, **kwargs):
        instance = Post.objects.select_related('category', 'source').prefetch_related('contents', 'keywords', 'liked_by').get(id=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        res_data = PostService.get_list_post_by_category(params)
        page = self.paginate_queryset(res_data)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(res_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=False, url_path="publish_post")
    def update_list_status_post(self, request, *args, **kwargs):
        post_ids = request.data.get('post_ids', [])
        PostService.update_status_post(post_ids)
        return Response({'message': 'Your changes have been saved.'}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, lookup_field="slug", url_path="content",
            serializer_class=PostSerializer)
    def slug(self, request, *args, **kwargs):
        instance = Post.objects.select_related('category', 'source').prefetch_related('contents', 'keywords').get(slug=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path="create_post", serializer_class=PostShortSerializer)
    def create_post(self, request, *args, **kwargs):
        bookmark = CrawlService.crawl_from_url_dantri()
        # bookmark = CrawlService.crawl_from_url_vietnamnet()
        CrawlService.craw_and_save_data_in_db(bookmark)
        return Response(bookmark, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path="like_post", serializer_class=PostSerializer, permission_class=[IsAuthenticated])
    def like_post(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user.user in post.liked_by.all():
            return Response({'message': 'You have already liked this post!'}, status=status.HTTP_400_BAD_REQUEST)
        post.likes += 1
        post.save()
        post.liked_by.add(request.user.user)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path="sort_like", serializer_class=PostSerializer)
    def get_post_by_like(self, request, *args, **kwargs):
        res_data = PostService.get_list_post_sort_like()
        page = self.paginate_queryset(res_data)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(res_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
