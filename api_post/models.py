from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from base.models import Base
from api_user.models import User
from .constants import PostStatus
import uuid
  
class Category(Base):
  title = models.CharField(default='', max_length=255)
  description = models.TextField()

  class Meta:
      db_table = "category"
      ordering = ('-created_at',)

class Source(Base):
  title = models.CharField(default='', max_length=255)
  domain = models.CharField(max_length=255, blank=True, unique=True)

  class Meta:
      db_table = "source"
      ordering = ('-created_at',)

class Post(Base):
  title = models.TextField(max_length=255, blank=True)
  slug = models.SlugField(unique=True, null=True)
  thumbnail = models.CharField(max_length=255, blank=True, null=True)
  category = models.ForeignKey(
      Category, related_name="posts", null=True, blank=True, on_delete=models.SET_NULL
  )
  source = models.OneToOneField(
    Source, related_name="posts", on_delete=models.SET_NULL, null=True, blank=True
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", blank=True, null=True)
  description = models.TextField(blank=True, null=True)
  likes = models.IntegerField(default=0)
  liked_by = models.ManyToManyField(User, related_name="liked_by", blank=True)
  publish_date = models.DateTimeField(default=timezone.now)
  author = models.CharField(max_length=255, blank=True)
  summary = models.CharField(max_length=255, blank=True)
  status = models.CharField(choices=PostStatus.choices(), default=PostStatus.PUBLISHED.value, max_length=50)
  views = models.IntegerField(default=0)

  def __str__(self):
    return self.title

  class Meta:
    db_table = "posts"
    ordering = ('-created_at',)

class PostVector(Base):
  post = models.OneToOneField(Post, on_delete=models.CASCADE)
  vector = models.BinaryField()

  class Meta:
    db_table = "post_vector"
    ordering = ('-created_at',)

class Keyword(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  keyword = models.CharField(max_length=255, blank=True)
  post = models.ForeignKey(
      Post, related_name="keywords", on_delete=models.CASCADE, null=True, blank=True
  )

  class Meta:
      db_table = "keyword"

class Contents(Base):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.TextField(max_length=255, blank=True)
  paragraph = models.JSONField(blank=True)
  description_img = models.TextField(blank=True)
  image = models.CharField(max_length=255, blank=True)
  post = models.ForeignKey(
    Post, related_name="contents", on_delete=models.CASCADE, null=True, blank=True
  )
  index = models.IntegerField(default=0)

  def __str__(self):
      return self.title

  class Meta:
      db_table = "contents"
      ordering = ('-created_at',)

