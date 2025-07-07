from django.urls import path
from .views import *
urlpatterns = [
    path('battle/request/', SendBattleRequestView.as_view()),
    path('battle/request/<uuid:pk>/accept/', AcceptBattleRequestView.as_view()),
    path('battle/<uuid:pk>/questions/', BattleQuestionsView.as_view()),
    path('battle/answer/', SubmitAnswerView.as_view()),
    path('battle/<uuid:pk>/finish/', FinishBattleView.as_view()),
    path('leaderboard/', LeaderboardView.as_view())
]