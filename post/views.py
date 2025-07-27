from rest_framework.response import Response
from django.db.models import F
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from .models import Post, PostView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from post.models import Post
from follower.models import Following

class UserPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer1
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_uid = self.kwargs['uid']
        queryset = Post.objects.filter(owner__uid=user_uid).order_by('-uploaded_at')

        for post in queryset:
            if not PostView.objects.filter(user=self.request.user, post=post).exists():
                PostView.objects.create(user=self.request.user, post=post)
                Post.objects.filter(pk=post.pk).update(views=F('views') + 1)

        return queryset


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = Following.objects.filter(user=user).values_list('following', flat=True)
        return Post.objects.filter(owner__in=following_users).order_by('-uploaded_at')


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# class PostRetrieveView(generics.RetrieveAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'uid'

class PostRetrieveView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # print(f"User {user} is accessing post {instance.uid}")  # ✅ Debug

        if not PostView.objects.filter(user=user, post=instance).exists():
            # print("New view - counting it")  # ✅ Debug
            PostView.objects.create(user=user, post=instance)
            instance.views += 1
            instance.save(update_fields=['views'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)




class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'uid'
    permission_classes = [IsAuthenticated]




class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only posts created by the current user
        return Post.objects.filter(owner=self.request.user).order_by('-uploaded_at')



class FollowingPostsWithCustomFilterView(generics.ListAPIView):

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Following users postlarini olish",
        operation_description="""
        Authenticated foydalanuvchi follow qilgan userlarning postlarini qaytaradi.

        **Filterlash:**
        - type parametri orqali post turini tanlash mumkin
        - Postlar eng yangi sanadan boshlab tartiblanadi

        **Authentication kerak:** Token yoki Session authentication
        """,
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Post turini tanlash (ixtiyoriy)",
                type=openapi.TYPE_STRING,
                enum=['image', 'video', 'text', 'words', 'youtube', 'fill_the_gap', 'make_sentence', 'question'],
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Muvaffaqiyatli javob",
                schema=PostSerializer(many=True)
            ),
            401: openapi.Response(description="Authentication talab qilinadi"),
            403: openapi.Response(description="Ruxsat yo'q")
        },
        tags=['Posts - Following']
    )
    def get(self, request, *args, **kwargs):
        """
        Following users postlarini qaytarish
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        post_type = self.request.query_params.get('type', None)


        following_users = Following.objects.filter(user=user).values_list('following', flat=True)


        queryset = Post.objects.filter(
            owner__in=following_users
        ).select_related('owner', 'quiz').order_by('-uploaded_at')


        if post_type:
            queryset = queryset.filter(type=post_type)

        return queryset


