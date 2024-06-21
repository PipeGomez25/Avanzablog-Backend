from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Like
from apps.posts.models import Post
from .serializers import LikeSerializer
from .pagination import LikesPagination
from apps.posts.utils import get_accessible_posts

class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    pagination_class = LikesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']
    queryset = Like.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        current_user = self.request.user
        accessible_posts = get_accessible_posts(current_user)
        post_id = self.request.query_params.get('post')
        if post_id:
            if not accessible_posts.filter(id=post_id).exists():
                self.permission_denied(self.request, message="Permission denied.")
        return Like.objects.filter(post_id__in=accessible_posts).distinct().order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        user = request.user
        post_id = request.data.get('post')
                
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=404)
        
        accessible_posts = get_accessible_posts(user)
        if post not in accessible_posts:
            return Response({"detail": "Permission denied."}, status=400)

        data = {'user': user.id, 'post': post.id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        like = get_object_or_404(Like, pk=self.kwargs['pk'])
        user = request.user
        post = like.post       
        accessible_posts = get_accessible_posts(user)
        if post not in accessible_posts:
            return Response({"detail": "Permission denied."}, status=403)
        if like.user != user and not user.is_admin:
            return Response({"detail": "You do not have permission to delete this like."}, status=403)
        like.delete()
        return Response({"detail": "Like deleted."}, status=204)
    
    def permission_denied(self, request, message=None, code=None):
        response_data = {"detail": message or "Permission denied."}
        response_status = status.HTTP_403_FORBIDDEN
        raise PermissionDenied(detail=response_data)