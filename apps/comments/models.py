from django.db import models
from apps.posts.models import Post
from apps.users.models import User

class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    comment = models.TextField(max_length=200, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

