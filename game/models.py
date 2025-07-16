from django.db import models
from django.contrib.auth.models import User
import uuid
from core import settings
from django.utils import timezone


class Word(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    transcript = models.CharField(max_length=200, null=True, blank=True)
    language = models.CharField(max_length=20, choices=[('english', 'English'), ('russian', 'Russian')])
    image = models.URLField(null=True, blank=True)
    type = models.CharField(max_length=100)  # essential_1_unit_2 kabi
    description = models.TextField(null=True, blank=True)
    collection_id = models.CharField(max_length=100)
    rate = models.IntegerField(default=0)
    level = models.CharField(max_length=10)  # A1, A2, B1, B2, C1, C2
    definition = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.word} ({self.language})"


class UserStatus(models.Model):
    STATUS_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
        ('ready', 'Ready'),
        ('in_battle', 'In Battle'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    total_score = models.IntegerField(default=0)
    battles_won = models.IntegerField(default=0)
    battles_lost = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class BattleRoom(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]

    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='battles_as_player1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='battles_as_player2')
    word_type = models.CharField(max_length=100)  # essential_1_unit_2
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    current_question = models.IntegerField(default=0)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='won_battles')

    def __str__(self):
        return f"Battle {self.room_id} - {self.player1.username} vs {self.player2.username}"


class BattleQuestion(models.Model):
    battle = models.ForeignKey(BattleRoom, on_delete=models.CASCADE, related_name='questions')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    correct_answer = models.CharField(max_length=200)
    player1_answer = models.CharField(max_length=200, null=True, blank=True)
    player2_answer = models.CharField(max_length=200, null=True, blank=True)
    player1_answer_time = models.DateTimeField(null=True, blank=True)
    player2_answer_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    asked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question {self.question_number} - {self.word.word}"


class BattleInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    word_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation from {self.from_user.username} to {self.to_user.username}"

