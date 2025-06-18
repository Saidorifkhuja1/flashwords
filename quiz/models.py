import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import datetime
from user.models import User


class Quiz(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    duration = models.DurationField(default=datetime.timedelta(minutes=30))
    questions = models.JSONField(help_text="""
        [
            {
                "question": "Savol matni",
                "options": ["A", "B", "C", "D"],
                "correct_option_index": 1
            },
            ...
        ]
    """)

    def clean(self):
        if not isinstance(self.questions, list):
            raise ValidationError("Questions must be a list.")

        if len(self.questions) > 100:
            raise ValidationError("You can add up to 100 questions.")

        for idx, question in enumerate(self.questions):
            if not isinstance(question, dict):
                raise ValidationError(f"Question at index {idx} must be a dictionary.")
            if 'question' not in question or 'options' not in question or 'correct_option_index' not in question:
                raise ValidationError(f"Question at index {idx} is missing required keys.")

            options = question['options']
            if not isinstance(options, list) or not (3 <= len(options) <= 6):
                raise ValidationError(f"Question at index {idx} must have 3 to 6 options.")

            correct_idx = question['correct_option_index']
            if not isinstance(correct_idx, int) or not (0 <= correct_idx < len(options)):
                raise ValidationError(f"Correct option index for question {idx} is invalid.")

    def __str__(self):
        return f"Quiz: {self.title} ({self.uid}) by {self.user.username}"
