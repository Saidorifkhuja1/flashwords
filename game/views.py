from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random
from .serializers import  *

class SendBattleRequestView(generics.CreateAPIView):
    queryset = BattleRequest.objects.all()
    serializer_class = BattleRequestSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class AcceptBattleRequestView(generics.GenericAPIView):
    serializer_class = BattleSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        req = BattleRequest.objects.get(uid=pk, receiver=request.user, accepted=False, is_active=True)
        req.accepted, req.is_active = True, False
        req.save()
        battle = Battle.objects.create(player1=req.sender, player2=req.receiver, level=req.level)
        words = list(Word.objects.filter(type=req.level))
        random.shuffle(words)
        for i, word in enumerate(words[:10]):
            BattleQuestion.objects.create(battle=battle, word=word, question_type=random.choice(['translate', 'write', 'listen']), order=i)
        return Response(BattleSerializer(battle).data, status=201)

class BattleQuestionsView(generics.GenericAPIView):
    serializer_class = BattleQuestionSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        battle = Battle.objects.get(uid=pk)
        questions = battle.questions.all().order_by('order')
        return Response(BattleQuestionSerializer(questions, many=True).data)

class SubmitAnswerView(generics.CreateAPIView):
    serializer_class = BattleAnswerSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        answer = serializer.save(user=self.request.user)
        answer.is_correct = answer.answer.strip().lower() == answer.question.word.eng.lower()
        answer.save()

class FinishBattleView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        battle = Battle.objects.get(uid=pk)
        if battle.is_finished:
            return Response({'detail': 'Already finished'})
        p1_score = BattleAnswer.objects.filter(question__battle=battle, user=battle.player1, is_correct=True).count()
        p2_score = BattleAnswer.objects.filter(question__battle=battle, user=battle.player2, is_correct=True).count()
        battle.player1_score, battle.player2_score, battle.is_finished = p1_score, p2_score, True
        s1, _ = UserStats.objects.get_or_create(user=battle.player1)
        s2, _ = UserStats.objects.get_or_create(user=battle.player2)
        s1.games_played += 1
        s2.games_played += 1
        if p1_score > p2_score:
            battle.winner = battle.player1
            s1.games_won += 1
            s2.games_lost += 1
            s1.total_points += 3
        elif p2_score > p1_score:
            battle.winner = battle.player2
            s2.games_won += 1
            s1.games_lost += 1
            s2.total_points += 3
        else:
            battle.is_draw = True
            s1.games_drawn += 1
            s2.games_drawn += 1
            s1.total_points += 1
            s2.total_points += 1
        s1.save(), s2.save(), battle.save()
        return Response({'winner': battle.winner.name if battle.winner else 'Draw'})

class LeaderboardView(generics.ListAPIView):
    serializer_class = UserStatsSerializer
    queryset = UserStats.objects.order_by('-total_points')[:10]