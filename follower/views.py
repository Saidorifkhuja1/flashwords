from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user.models import User
from rest_framework.exceptions import NotFound
from .models import Follower, Following
from .serializers import FollowerSerializer, FollowingSerializer, UserSerializer, EmptySerializer
from django.db.models import Q


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(role__iexact='teacher').exclude(uid=current_user.uid)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def post(self, request, uid):
        try:
            to_follow = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        if to_follow == request.user:
            return Response({'detail': "You can't follow yourself."}, status=400)

        # Prevent duplicates
        Follower.objects.get_or_create(user=to_follow, follower=request.user)
        Following.objects.get_or_create(user=request.user, following=to_follow)

        return Response({'detail': f'You are now following {to_follow.name}.'}, status=200)


class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer
    def post(self, request, uid):
        try:
            to_unfollow = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        Follower.objects.filter(user=to_unfollow, follower=request.user).delete()
        Following.objects.filter(user=request.user, following=to_unfollow).delete()

        return Response({'detail': f'You have unfollowed {to_unfollow.name}.'}, status=200)


class ListFollowersView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follower.objects.filter(user=self.request.user)


class ListFollowingView(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Following.objects.filter(user=self.request.user)



class RemoveFollowerAPIView(generics.DestroyAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Follower.objects.filter(user=self.request.user)

    def get_object(self):
        follower_uid = self.kwargs.get("uid")
        try:
            return Follower.objects.get(user=self.request.user, follower__uid=follower_uid)
        except Follower.DoesNotExist:
            raise NotFound("Follower not found.")



