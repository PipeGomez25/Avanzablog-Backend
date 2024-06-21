import factory
from factory import SubFactory
from apps.users.models import Team, User

class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    tname = factory.Sequence(lambda n: f"Team {n}")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    is_admin = False
    is_staff = False
    is_superuser = False