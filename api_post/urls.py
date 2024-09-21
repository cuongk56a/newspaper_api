from rest_framework_extensions.routers import DefaultRouter
from django.urls import path, include
from api_post.views import PostViewSet, CategoryViewSet, SourceViewSet
from rest_framework_nested import routers

app_name = "api_post"
router = DefaultRouter()
router.register(r'source', SourceViewSet, basename='source')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'post', PostViewSet, basename='post')

urlpatterns = [
    path(r'', include(router.urls)),
]
