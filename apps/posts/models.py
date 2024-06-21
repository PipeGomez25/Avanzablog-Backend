from django.db import models
from apps.users.models import User

class Categories(models.Model):
    category_name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(max_length=1000, blank=False)
    excerpt = models.TextField(max_length=200, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    permissionsPost = models.ManyToManyField(Categories, through = 'Permission', related_name = 'permissions_post')
    
    def save(self, *args, **kwargs):
        if not self.excerpt:
            self.excerpt = self.content[:200]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Permission(models.Model):
    OPTIONS = [
        ('read', 'Read'),
        ('read_edit', 'Read & Edit'),
        ('none', 'None')
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='permissions_set') 
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, default=1)
    access = models.CharField(max_length=20, choices=OPTIONS)
    
 
 