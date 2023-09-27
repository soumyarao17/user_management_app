from django.contrib.auth.base_user import BaseUserManager

from app.constants import UserStatus, ROLE_CHOICES, RoleChoices
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from bcrypt import checkpw, gensalt, hashpw
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, username, password, role, **extra_fields):
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        if extra_fields.get('role') != RoleChoices.ADMIN:
            raise ValueError('Superuser must be admin!')

        return self.create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        if extra_fields.get('role') != RoleChoices.ADMIN:
            raise ValueError('Superuser must be admin!')

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RoleChoices.USER)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    def _str_(self):
        return self.username

    @staticmethod
    def generate_password_hash(password):
        password_bytes = password.encode('utf-8')
        generated_salt = gensalt()
        password_hash = hashpw(password_bytes, generated_salt)
        return password_hash

    def set_password(self, password):
        password_hash = self.generate_password_hash(password)
        self.password = password_hash.decode('utf-8')

    def check_password(self, password):
        if checkpw(password.encode('utf-8'), self.password.encode('utf-8')):
            return True
        return False

    def log_in(self, password):
        if self.password and not self.check_password(password):
            # Already Registered user with wrong credentials
            return False
        self.is_active = True
        # No password set -> User Registration OR password match
        return True

    def log_out(self):
        self.is_active = False
        return True

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN

    def save(self, *args, **kwargs):
        # Add validation such as if user already exists
        if User.objects.filter(role__in=[RoleChoices.ADMIN]).count() == 0:
            self.role = RoleChoices.ADMIN
            self.status = UserStatus.ACTIVATED
            print("This user is set up as ADMIN role by default as there are no other admin roles.")
        return super(User, self).save(*args, **kwargs)


class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    app = models.CharField(max_length=255, blank=True)
    details = models.TextField(blank=True)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.id} : {self.title}"


class Note(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.id} : {self.title}"
