from django.db import models
from user.models import User

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_from_follower')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'follower')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower} follows {self.user} [Follower]'


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_from_following')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} follows {self.following} [Following]'
