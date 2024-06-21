from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from .serializers import PermissionsSerializer, post_serializer
from .models import Post, Permission, Categories
from apps.users.models import User
from .permissions import CanViewPost
from .pagination import PostsPagination
from .utils import get_accessible_posts

class list_posts_view(generics.ListCreateAPIView):
    serializer_class = post_serializer
    pagination_class = PostsPagination
    
    def get_permissions(self):
        if self.request.method=='POST': 
            return [IsAuthenticated()]                    
        if self.request.method=='GET':
            return [AllowAny()]
    
    def get_queryset(self):
        current_user = self.request.user
        return get_accessible_posts(current_user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [CanViewPost]
    queryset = Post.objects.all()
    serializer_class = post_serializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "post deleted"}, status=status.HTTP_204_NO_CONTENT)
