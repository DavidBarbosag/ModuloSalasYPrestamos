from django.db import models

class RecreativeElement(models.Model):

    id = models.CharField(primary_key=True, max_length=15, blank=False)


