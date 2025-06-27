from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Voice
from .serializers import VoiceSerializer


class VoiceListView(generics.ListAPIView):
    queryset = Voice.objects.all().order_by('-created_at')
    serializer_class = VoiceSerializer
    permission_classes = [IsAuthenticated]


class VoiceCreateView(generics.CreateAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()  # If you later add `author`, then use: serializer.save(author=self.request.user)


class VoiceRetrieveView(generics.RetrieveAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'


class VoiceUpdateView(generics.UpdateAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    parser_classes = [MultiPartParser, FormParser]


class VoiceDeleteView(generics.DestroyAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
