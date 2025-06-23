from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from user.models import User
from quiz.models import Quiz

class Post(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('post', 'Post'),
        ('quiz', 'Quiz'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, null=True, blank=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='post', null=True, blank=True)
    image_video = models.FileField(upload_to='news/', null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    uploaded_at = models.DateTimeField(default=timezone.now)
    views = models.IntegerField(default=0)

    def clean(self):
        if self.content_type == 'quiz' and not self.quiz:
            raise ValidationError({"quiz": "Quiz must be provided if content_type is 'quiz'."})

        if self.content_type == 'post' and not self.image_video:
            raise ValidationError({"image_video": "Image or video must be provided if content_type is 'post'."})

        if self.image_video:
            file_type = self.image_video.file.content_type
            valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
            valid_video_types = ['video/mp4', 'video/webm', 'video/ogg']

            if self.type == "image" and file_type not in valid_image_types:
                raise ValidationError({"image_video": "Uploaded file must be an image."})
            elif self.type == "video" and file_type not in valid_video_types:
                raise ValidationError({"image_video": "Uploaded file must be a video."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')




