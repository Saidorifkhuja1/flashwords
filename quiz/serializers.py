from rest_framework import serializers
from .models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['uid', 'title', 'questions']
        read_only_fields = ['uid']

    def validate_questions(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Questions must be a list.")
        if len(value) > 100:
            raise serializers.ValidationError("You can add up to 100 questions.")

        for idx, q in enumerate(value):
            if 'question' not in q or 'options' not in q or 'correct_option_index' not in q:
                raise serializers.ValidationError(f"Question at index {idx} is missing required keys.")
            options = q['options']
            if not isinstance(options, list) or not (3 <= len(options) <= 6):
                raise serializers.ValidationError(f"Question at index {idx} must have 3 to 6 options.")
            if not isinstance(q['correct_option_index'], int) or not (0 <= q['correct_option_index'] < len(options)):
                raise serializers.ValidationError(f"Correct option index for question {idx} is invalid.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Quiz.objects.create(user=user, **validated_data)
