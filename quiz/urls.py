from django.urls import path
from .views import *

urlpatterns = [
       path('quiz_create/', QuizCreateAPIView.as_view()),
       path('quiz_list/', QuizListView.as_view()),
       path('my_quizzes/', MyQuizListView.as_view()),
       path('quiz_details/<uuid:uid>/', QuizRetrieveView.as_view()),
       path('quiz_update/<uuid:uid>/', QuizUpdateView.as_view()),
       path('quiz_delete/<uuid:uid>/', QuizDeleteView.as_view()),

]


