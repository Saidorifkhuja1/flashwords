from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from follower.models import Following
from .serializers import *

class UserPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer1

    def get_queryset(self):
        user_uid = self.kwargs['uid']
        return Post.objects.filter(owner__uid=user_uid).order_by('-uploaded_at')






class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Validate before saving"""
        serializer.save()


class PostRetrieveView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'uid'
    # permission_classes = [IsAdminUser]


class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        """Validate before saving"""
        serializer.save()


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'uid'
    permission_classes = [IsAuthenticated]


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current user
        user = self.request.user

        # Get all users the current user is following
        following_users = Following.objects.filter(user=user).values_list('following', flat=True)

        # Return News objects created by the followed users
        return Post.objects.filter(owner__in=following_users).order_by('-uploaded_at')

class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only posts created by the current user
        return Post.objects.filter(owner=self.request.user).order_by('-uploaded_at')