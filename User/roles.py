from django.db import models

class roles(models.TextChoices):
    STUDENT = 'STUDENT'
    ADMIN = 'ADMIN'
    FUNCTIONARY = 'FUNCTIONARY'
    TEACHER = 'TEACHER'
    MANAGER = 'MANAGER'
    GENERALSERVICES = 'GENERALSERVICES'
