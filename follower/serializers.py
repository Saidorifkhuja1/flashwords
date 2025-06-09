from rest_framework import serializers
from user.models import User
from .models import Follower, Following

class UserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['uid', 'name', 'last_name', 'email', 'role', 'status', 'avatar', 'mini_avatar', 'is_following']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follower.objects.filter(user=obj, follower=request.user).exists()
        return False




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


class EmptySerializer(serializers.Serializer):
    pass


