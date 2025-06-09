from django.urls import path
from .views import *

urlpatterns = [
       path('quiz_create/', QuizCreateAPIView.as_view()),
       path('my_quizzes/', MyQuizListView.as_view()),
       path('quiz_details/<uuid:pk>/', QuizRetrieveView.as_view()),
       path('quiz_update/<uuid:pk>/', QuizUpdateView.as_view()),
       path('quiz_delete/<uuid:pk>/', QuizDeleteView.as_view()),

]
