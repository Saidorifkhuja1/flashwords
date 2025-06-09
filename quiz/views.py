from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsTeacher
from .models import Quiz
from .serializers import QuizSerializer

class QuizCreateAPIView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

