from rest_framework import serializers
from django.core.exceptions import ValidationError
from user.serializers import UserProfileSerializer
from .models import Post
from quiz.models import Quiz


class PostSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    quiz = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['uid', 'title', 'body', 'type', 'image_video', 'uploaded_at', 'owner', 'content_type', 'quiz']

    def get_quiz(self, obj):
        if obj.content_type == 'quiz' and obj.quiz:
            return str(obj.quiz.uid)
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    image_video = serializers.FileField(required=False)
    quiz = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ['uid', 'title', 'body', 'type', 'image_video', 'content_type', 'quiz']

    def validate(self, data):
        content_type = data.get('content_type')
        image_video = data.get('image_video')
        quiz_uid = data.get('quiz')
        news_type = data.get("type")

        # Quiz content validation
        if content_type == 'quiz':
            if not quiz_uid:
                raise ValidationError({"quiz": "This field is required for quiz content."})
            try:
                quiz_instance = Quiz.objects.get(uid=quiz_uid)
            except Quiz.DoesNotExist:
                raise ValidationError({"quiz": "Quiz with this UID does not exist."})
            data['quiz'] = quiz_instance
            data['image_video'] = None  # ignore media if it's a quiz

        # Post content validation
        elif content_type == 'post':
            if not image_video:
                raise ValidationError({"image_video": "This field is required for post content."})

            valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
            valid_video_types = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv']
            file_type = image_video.content_type

            if news_type == "image" and file_type not in valid_image_types:
                raise ValidationError({"image_video": "Uploaded file must be an image."})
            elif news_type == "video" and file_type not in valid_video_types:
                raise ValidationError({"image_video": "Uploaded file must be a video."})

            data['quiz'] = None  # ensure no quiz is linked for normal post

        else:
            raise ValidationError({"content_type": "Invalid content type. Must be 'post' or 'quiz'."})

        return data


class PostSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['uid', 'title', 'body', 'type', 'image_video', 'uploaded_at', 'content_type', 'quiz']

        def get_quiz(self, obj):
            if obj.content_type == 'quiz' and obj.quiz:
                return str(obj.quiz.uid)
            return None

