import uuid
from django.core.validators import *
from django.db import models
from django.utils import timezone


class Article(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=250)
    body = models.TextField(max_length=2500000000, blank=True, null=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


