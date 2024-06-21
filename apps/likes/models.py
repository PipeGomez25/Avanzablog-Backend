from django.db import models
from apps.posts.models import Post
from apps.users.models import User

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False,related_name='postlike')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False,related_name='userlike')
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        unique_together = ('post', 'user')

