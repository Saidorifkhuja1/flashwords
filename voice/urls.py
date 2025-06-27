from django.urls import path
from .views import *

urlpatterns = [
    path('voices/', VoiceListView.as_view()),
    path('voices/create/', VoiceCreateView.as_view()),
    path('voices/<uuid:uid>/', VoiceRetrieveView.as_view()),
    path('voices/<uuid:uid>/update/', VoiceUpdateView.as_view()),
    path('voices/<uuid:uid>/delete/', VoiceDeleteView.as_view()),
]
