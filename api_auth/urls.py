from django.urls import path
from rest_framework_extensions.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from .views import register_user, login, token_refresh

app_name = "api_auth"
router = DefaultRouter()

_urlpatterns = [
  path('register/', csrf_exempt(register_user), name="register_user"),
  path('login/', csrf_exempt(login), name="login"),
  path('token/refresh/', csrf_exempt(token_refresh), name='token_refresh'),
]

urlpatterns = router.urls + _urlpatterns