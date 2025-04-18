from django.urls import path
from .views import FollowUserView, UnfollowUserView, ListFollowersView, ListFollowingView, RemoveFollowerAPIView

urlpatterns = [
    path('follow/<uuid:uid>/', FollowUserView.as_view()),
    path('unfollow/<uuid:uid>/', UnfollowUserView.as_view()),
    path('my_followers/', ListFollowersView.as_view()),
    path('my_followings/', ListFollowingView.as_view()),
    path("remove_follower/<uuid:uid>/", RemoveFollowerAPIView.as_view()),
]


