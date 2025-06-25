import uuid
from django.core.validators import *
from django.db import models
from django.utils import timezone


class Book(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=250, blank=True, null=True)
    author = models.CharField(max_length=250, blank=True, null=True)
    pdf = models.FileField(upload_to='books/', validators=[FileExtensionValidator(['pdf'])])
    cover_image = models.ImageField(upload_to='books/covers/', default=False, blank=True, null=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title




