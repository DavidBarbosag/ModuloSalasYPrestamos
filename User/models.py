from django.contrib.auth.models import AbstractUser, Group, Permission 
from django.db import models
from User.roles import roles
from RecreativeElement.models import RecreativeElement

class User(AbstractUser):
    id = models.CharField(primary_key=True, max_length=15, blank=False)
    idNum = models.CharField(max_length=15, blank=False, unique=True)
    name = models.CharField(max_length=150, blank=False)
    email = models.CharField(max_length=150, blank=False, unique=True)
    role = models.CharField(max_length=25, choices=roles.choices, blank=False)
    profile = models.CharField(max_length=25, choices=roles.choices, default=roles.STUDENT, blank=True)
    recreativeElements = models.ManyToManyField(
        RecreativeElement,
        related_name='users',
        blank=True
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions_set',
        related_query_name='user',
    )

    def __str__(self):
        return f"{self.id} - {self.name}"