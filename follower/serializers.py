from rest_framework import serializers
from user.models import User
from .models import Follower, Following

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'name', 'last_name', 'email', 'role', 'status', 'avatar', 'mini_avatar']



class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'name', 'last_name', 'avatar']

class FollowerSerializer(serializers.ModelSerializer):
    follower = UserSimpleSerializer()

    class Meta:
        model = Follower
        fields = ['follower', 'created_at']

class FollowingSerializer(serializers.ModelSerializer):
    following = UserSimpleSerializer()

    class Meta:
        model = Following
        fields = ['following', 'created_at']
