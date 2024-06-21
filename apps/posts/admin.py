from django.contrib import admin
from .models import Post, Permission, Categories

admin.site.register(Post)
admin.site.register(Permission)
admin.site.register(Categories)