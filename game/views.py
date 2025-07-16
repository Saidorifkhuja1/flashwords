from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserStatus, Word
from .serializers import UserStatusSerializer, WordSerializer


class LeaderboardView(generics.ListAPIView):
    serializer_class = UserStatusSerializer

    def get_queryset(self):
        return UserStatus.objects.all().order_by('-total_score')[:10]


@api_view(['GET'])
def user_stats(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_status = UserStatus.objects.get(user=user)
        serializer = UserStatusSerializer(user_status)
        return Response(serializer.data)
    except (User.DoesNotExist, UserStatus.DoesNotExist):
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_words_by_type(request, word_type):
    words = Word.objects.filter(type=word_type)
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)

