from django.urls import path
from .views import *

urlpatterns = [
    path('posts_list/', PostListView.as_view()),
    path('post_create/', PostCreateView.as_view()),
    path('post_detail/<uuid:uid>/', PostRetrieveView.as_view()),
    path('update_post/<uuid:uid>/', PostUpdateView.as_view()),
    path('delete_post/<uuid:uid>/', PostDeleteView.as_view()),
    path('my_posts/', MyPostListView.as_view()),
    path('users/<uuid:uid>/posts/', UserPostsAPIView.as_view()),
]