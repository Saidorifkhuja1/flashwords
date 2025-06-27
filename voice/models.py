import uuid
from django.db import models
from django.utils import timezone



class Voice(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='voice/images/', blank=True, null=True)
    time = models.CharField(max_length=50, help_text="Audio length, e.g. '3:20'")
    audio_url = models.FileField(upload_to='voice/audios/')
    data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

