from rest_framework import serializers
from .models import Like
from apps.posts.utils import get_accessible_posts

class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post', 'user']

    def create(self, validated_data):
        user = validated_data.get('user')
        post = validated_data.get('post')

        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            raise serializers.ValidationError({"detail": "Like already exists."})
        
        return like