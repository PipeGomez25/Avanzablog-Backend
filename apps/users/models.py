from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def _create_user(self, username, email, is_admin, team, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_admin=is_admin,
            team=team,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, team=None, password=None, **extra_fields):
        return self._create_user(username, email, False, team, password, False, False, **extra_fields)

    def create_adminuser(self, username, email, team=None, password=None, **extra_fields):
        return self._create_user(username, email, True, team, password, False, False, **extra_fields)

    def create_superuser(self, username, email, team=None, password=None, **extra_fields):
        return self._create_user(username, email, True, team, password, True, True, **extra_fields)

class Team(models.Model):
    tname=models.CharField(unique = True, max_length = 255)
    
    def __str__(self):
        return self.tname

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField('Correo Electrónico', max_length=255, unique=True)
    is_admin = models.BooleanField('role', default=False)
    team = models.ForeignKey(Team, on_delete=models.SET_DEFAULT, default=1)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

@receiver(pre_save, sender=User)
def create_team_for_user(sender, instance: User, **kwargs):
    if not Team.objects.filter(pk=1).first():
        Team.objects.create(id=1, tname='Default Team')
