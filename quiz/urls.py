from django.urls import path
from .views import *

urlpatterns = [
       path('quiz/create/', QuizCreateAPIView.as_view()),

]
