import factory
from factory.django import DjangoModelFactory
from .models import Categories, Post, Permission
from apps.users.factories import UserFactory

class CategoriesFactory(DjangoModelFactory):
    class Meta:
        model = Categories

    category_name = factory.Iterator(['Public', 'Authenticated', 'Team', 'Author'])

class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')
    excerpt = factory.LazyAttribute(lambda obj: obj.content[:200])

    @factory.post_generation
    def permissions_set(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for permission_data in extracted:
                Permission.objects.create(post=self, **permission_data)
        else:
            categories = Categories.objects.bulk_create([
                Categories(category_name='Public'),
                Categories(category_name='Authenticated'),
                Categories(category_name='Team'),
                Categories(category_name='Author'),
            ])
            for category in categories:
                Permission.objects.create(post=self, category=category, access='read')

class PermissionFactory(DjangoModelFactory):
    class Meta:
        model = Permission

    post = factory.SubFactory(PostFactory)
    category = factory.SubFactory(CategoriesFactory)
    access = 'read'