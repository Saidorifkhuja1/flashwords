
from django.urls import path
from .views import BookListAPIView, BookDetailAPIView

urlpatterns = [
    path('books/', BookListAPIView.as_view()),
    path('books/<uuid:uid>/', BookDetailAPIView.as_view()),
]

