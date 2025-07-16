from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('api/user-stats/<int:user_id>/', views.user_stats, name='user_stats'),
    path('api/words/<str:word_type>/', views.get_words_by_type, name='words_by_type'),
]