import factory
from apps.comments.models import Comments
from apps.posts.factories import PostFactory
from apps.users.factories import UserFactory

class CommentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comments

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
    comment = factory.Faker('sentence', nb_words=10)
