from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from base.models import Base
from .constants import Roles
from .manager import UserManager
import uuid

# Create your models here.
class Account(AbstractUser):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
  email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  
  username = None
  first_name = None
  last_name = None
  
  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = []
  class Meta: 
    db_table = 'accounts'
    ordering = ('date_joined',)

  def __str__(self):
        return str(self.email)

  def tokens(self):
      refresh = RefreshToken.for_user(self)
      return {
          'refresh': str(refresh),
          'access': str(refresh.access_token)
      }
  
class User(Base):
  full_name = models.CharField(max_length=100, null=False)
  avatar = models.CharField(max_length=200, null=True, blank=True)
  role = models.CharField(choices=Roles.choices(), default=Roles.USER.value, max_length=50)
  address = models.TextField(null=True, blank=True)
  phone = models.CharField(max_length=20, null=True, blank=True)
  birthday = models.DateField(null=True, blank=True)
  account = models.OneToOneField('Account', on_delete=models.CASCADE, related_name="user")

  class Meta:
      db_table = "users"
      ordering = ('-created_at',)
