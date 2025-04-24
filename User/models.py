from django.contrib.auth.models import AbstractUser
from django.db import models
from User.roles import roles
from RecreativeElement.models import RecreativeElement


class User(AbstractUser):
    """
    Represents a system user.

    Attributes:
        id (str): Unique identifier for the user (used as the primary key).
        idNum (str): Identification number of the user.
        name (str): Full name of the user.
        email (str): User's email address.
        role (str): Role of the user in the system (student, admin, or functionary).
        profile (str): Optional user profile (defaults to student).
        recreativeElements (ManyToMany[RecreativeElement]): Recreational elements associated with the user.
    """
    id = models.CharField(primary_key=True,max_length=15, blank=False)
    idNum = models.CharField(max_length=15, blank=False)
    name = models.CharField(max_length=150, blank=False)
    email = models.CharField(max_length=150, blank=False)
    role = models.CharField(max_length=25, choices = roles.choices, blank=False)
    profile = models.CharField(max_length=25, choices = roles.choices, default=roles.STUDENT, blank=True)
    recreativeElements= models.ManyToManyField(
        RecreativeElement,
        related_name='users',
        blank=True
    )


    def __str__(self):
        """
        Returns a string representation of the user.

        Returns:
            str: The user's name.
        """
        return f"{self.id} - {self.name}"