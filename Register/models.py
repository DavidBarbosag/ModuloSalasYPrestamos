from django.db import models

class Register(models.Model):

    id = models.CharField(primary_key=True, max_length=15, blank=False)

    def __str__(self):
        return f"{self.id}"
