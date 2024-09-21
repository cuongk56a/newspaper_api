from django.urls import path
from rest_framework_extensions.routers import DefaultRouter
from .views import UserViewSet

app_name = "api_user"
router = DefaultRouter()

router.register(r"", UserViewSet, basename="user")

urlpatterns = router.urls