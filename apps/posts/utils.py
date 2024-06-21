from django.db.models import Prefetch, Q
from .models import Post, Permission
from apps.users.models import User

def filter_permissions(category_name, access_list):
    return Permission.objects.filter(category__category_name=category_name, access__in=access_list)

def get_accessible_posts(user):
    if not user.is_authenticated:
        permission_filtered = filter_permissions('Public', ['read', 'read_edit'])
        permissions_prefetch = Prefetch('permissions_set', queryset=permission_filtered)
        return Post.objects.prefetch_related(permissions_prefetch).filter(
            permissions_set__in=permission_filtered).distinct().order_by('-timestamp')

    elif user.is_admin:
        return Post.objects.all().order_by('-timestamp')

    else:
        
        permission_filtered = filter_permissions('Author', ['read', 'read_edit'])
        permissions_prefetch = Prefetch('permissions_set', queryset=permission_filtered)
        Author = Post.objects.prefetch_related(permissions_prefetch).filter(author=user, permissions_set__in=permission_filtered).distinct()

        permission_filtered = filter_permissions('Team', ['read', 'read_edit'])
        permissions_prefetch = Prefetch('permissions_set', queryset=permission_filtered)
        team_members = User.objects.filter(team=user.team).exclude(id=user.id)
        Team = Post.objects.prefetch_related(permissions_prefetch).filter(
            author__in=team_members, permissions_set__in=permission_filtered).distinct()

        permission_filtered = filter_permissions('Authenticated', ['read', 'read_edit'])
        permissions_prefetch = Prefetch('permissions_set', queryset=permission_filtered)
        Authenticated = Post.objects.prefetch_related(permissions_prefetch).filter(
            permissions_set__in=permission_filtered).exclude(
            Q(author=user) | Q(author__in=team_members)
        ).distinct()
        Accesible_post=Author | Team | Authenticated
        return Accesible_post.order_by('-timestamp')