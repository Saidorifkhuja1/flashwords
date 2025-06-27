from rest_framework import serializers
from .models import Voice


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'
        read_only_fields = ['uid', 'created_at']
