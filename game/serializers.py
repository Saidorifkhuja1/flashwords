from rest_framework import serializers
from .models import *

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class BattleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleRequest
        fields = '__all__'
        read_only_fields = ('sender', 'accepted', 'is_active')

class BattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Battle
        fields = '__all__'

class BattleQuestionSerializer(serializers.ModelSerializer):
    word = WordSerializer()
    class Meta:
        model = BattleQuestion
        fields = ['uid', 'word', 'question_type', 'order']

class BattleAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleAnswer
        fields = '__all__'
        read_only_fields = ('user', 'is_correct', 'answered_at')

class UserStatsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = UserStats
        fields = '__all__'


class EmptySerializer(serializers.Serializer):
    class Meta:
        ref_name = "FollowerEmptySerializer"