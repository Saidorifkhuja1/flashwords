from rest_framework import serializers
from django.core.exceptions import ValidationError
from user.serializers import UserProfileSerializer
from .models import Post
from quiz.models import Quiz


from rest_framework import serializers
from user.serializers import UserProfileSerializer
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    quiz = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'uid', 'title', 'body', 'type', 'image_video',
            'uploaded_at', 'owner', 'content_type', 'quiz', 'views'
        ]

    def get_quiz(self, obj):
        if obj.content_type == 'quiz' and obj.quiz:
            return str(obj.quiz.uid)
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    image_video = serializers.FileField(required=False, allow_null=True)
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
            # image_video is optional for quiz - don't set to None

        # Post content validation
        elif content_type == 'post':
            # image_video is now optional for post content too
            if quiz_uid:
                data['quiz'] = None  # Clear quiz for post content

        # File type validation - only if file is provided
        if image_video:
            valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
            valid_video_types = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv']
            file_type = image_video.content_type

            if news_type == "image" and file_type not in valid_image_types:
                raise ValidationError({"image_video": "Uploaded file must be an image."})
            elif news_type == "video" and file_type not in valid_video_types:
                raise ValidationError({"image_video": "Uploaded file must be a video."})

        return data



class PostSerializer1(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['uid', 'title', 'body', 'type', 'image_video', 'uploaded_at', 'content_type', 'quiz']

    def get_quiz(self, obj):
        if obj.content_type == 'quiz' and obj.quiz:
            return str(obj.quiz.uid)
        return None




