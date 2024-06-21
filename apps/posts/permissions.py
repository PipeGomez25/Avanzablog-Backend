from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Permission
from apps.users.models import User
from apps.posts.models import Post

class CanViewPost(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        relatedPost = obj.post if hasattr(obj, 'post') else obj
        relatedAuthor = relatedPost.author
        
        try:
            ispublic = Permission.objects.get(post=obj, category__category_name='Public')
        except Permission.DoesNotExist:
            ispublic = None
        
        try:
            isauthenticated = Permission.objects.get(post=obj, category__category_name='Authenticated')
        except Permission.DoesNotExist:
            isauthenticated = None
        
        try:
            isteam = Permission.objects.get(post=obj, category__category_name='Team')
        except Permission.DoesNotExist:
            isteam = None
        
        try:
            isauthor = Permission.objects.get(post=obj, category__category_name='Author')
        except Permission.DoesNotExist:
            isauthor = None

        if request.method in ['GET']:
            if not request.user.is_authenticated:
                if ispublic and ispublic.access in ['read', 'read_edit']:
                    return True
                raise NotFound
            
            if request.user.is_admin:
                return True
                
            if request.user.id == relatedPost.author.id:
                if isauthor and isauthor.access in ['read', 'read_edit']:
                    return True
                raise NotFound

            if request.user.team == relatedAuthor.team:
                if isteam and isteam.access in ['read', 'read_edit']:
                    return True
                raise NotFound

            if request.user.is_authenticated:
                if isauthenticated and isauthenticated.access in ['read', 'read_edit']:
                    return True
                raise NotFound
                   

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if not request.user.is_authenticated:
                if ispublic and ispublic.access == 'read_edit':
                    return True
                raise PermissionDenied
            
            if request.user.is_admin:
                return True

            if request.user.id == relatedPost.author.id:
                if isauthor and isauthor.access == 'read_edit':
                    return True
                raise PermissionDenied

            if request.user.team == relatedAuthor.team:
                if isteam and isteam.access == 'read_edit':
                    return True
                raise PermissionDenied

            if request.user.is_authenticated:
                if isauthenticated and isauthenticated.access == 'read_edit':
                    return True
                raise PermissionDenied
        return False
