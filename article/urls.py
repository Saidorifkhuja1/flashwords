from django.urls import path
from .views import ArticleListAPIView, ArticleDetailAPIView

urlpatterns = [
    path('articles/', ArticleListAPIView.as_view()),
    path('article/<uuid:uid>/', ArticleDetailAPIView.as_view()),
]

