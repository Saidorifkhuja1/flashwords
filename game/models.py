from django.db import models
import uuid
from user.models import User

class Word(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    TYPE = [('a1', 'A1'), ('a2', 'A2'), ('b1', 'B1'), ('b2', 'B2'), ('c1', 'C1'), ('c2', 'C2')]
    uzb = models.CharField(max_length=400)
    eng = models.CharField(max_length=400)
    type = models.CharField(max_length=10, choices=TYPE)

    def __str__(self):
        return self.uzb



class BattleRequest(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    level = models.CharField(max_length=10, choices=Word.TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.sender


class Battle(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_player2')
    level = models.CharField(max_length=10, choices=Word.TYPE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_battles')
    is_draw = models.BooleanField(default=False)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.level


class BattleQuestion(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='questions')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=20, choices=[('translate', 'Translate'), ('write', 'Write'), ('listen', 'Listen')])
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.battle


class BattleAnswer(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    question = models.ForeignKey(BattleQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class UserStats(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    games_drawn = models.IntegerField(default=0)

    def __str__(self):
        return self.user

