from rest_framework import serializers
from user.models import User
from .models import Follower, Following

class UserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    username = serializers.CharField(allow_null=True, required=False)
    bio = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = [
            'uid', 'name', 'last_name', 'email', 'username', 'bio',
            'role', 'status', 'avatar', 'mini_avatar', 'is_following'
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follower.objects.filter(user=obj, follower=request.user).exists()




class UserSimpleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(allow_null=True, required=False)
    bio = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['uid', 'name', 'last_name', 'username', 'bio', 'avatar']

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


