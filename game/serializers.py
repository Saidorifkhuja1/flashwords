from rest_framework import serializers
from .models import UserStatus, Word


class UserStatusSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    total_battles = serializers.SerializerMethodField()

    class Meta:
        model = UserStatus
        fields = ['username', 'total_battles', 'battles_won', 'battles_lost', 'total_score']

    def get_total_battles(self, obj):
        return obj.battles_won + obj.battles_lost


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['uid', 'word', 'translation', 'transcript', 'language', 'image', 'type', 'level', 'definition']



