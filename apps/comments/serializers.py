from rest_framework import serializers
from django.db import transaction
from .models import Comments
from apps.posts.utils import get_accessible_posts

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'post', 'user', 'comment', 'timestamp']
        read_only_fields = ['timestamp']
    
    @transaction.atomic
    def create(self, validated_data):
        user = validated_data.get('user')
        post = validated_data.get('post')
        comment = validated_data.get('comment')
        
        Comment = Comments.objects.create(user=user, post=post, comment=comment)
        return Comment