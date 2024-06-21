import factory
from factory.django import DjangoModelFactory
from apps.posts.factories import PostFactory
from apps.users.factories import UserFactory
from .models import Like

class LikeFactory(DjangoModelFactory):
    class Meta:
        model = Like
        django_get_or_create = ('post', 'user')

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)