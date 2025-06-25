
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['uid', 'title', 'pdf', 'cover_image', 'author', 'views', 'created_at']

