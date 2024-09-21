from django.db import models
from django.db.models import Manager
# from django.utils import timezone
import uuid

# Create your models here.
class Base(models.Model):
  objects = Manager
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
      abstract = True