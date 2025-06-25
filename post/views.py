from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from follower.models import Following
from .serializers import *
from .models import Post, PostView

class UserPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer1
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_uid = self.kwargs['uid']
        return Post.objects.filter(owner__uid=user_uid).order_by('-uploaded_at')



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


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.all().order_by('-uploaded_at')


class MyPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only posts created by the current user
        return Post.objects.filter(owner=self.request.user).order_by('-uploaded_at')


