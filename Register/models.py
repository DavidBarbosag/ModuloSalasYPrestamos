from django.db import models
from Reservation.models import Reservation

class Register(models.Model):
    """
       Represents a register .

       Attributes:
            registerID (int): Unique identifier for the Register (used as the primary key).
            reservationID (str): Unique identifier of the Reservation.
            remainingElements (JSONField): JSONField of the remaining elements represented as follows
            {'codigo': str, 'nombre': str, 'estado': str, 'cantidad': int}
            returnedElements (JSONField): JSONField of the returned elementsrepresented as follows
            {'codigo': str, 'nombre': str, 'estado': str, 'cantidad': int}

       """

    class StatusChoices(models.TextChoices):
        RETURNED_GOOD = 'RETURNED_GOOD', 'Returned in Good Condition'
        RETURNED_DAMAGED = 'RETURNED_DAMAGED', 'Returned Damaged'
        NOT_RETURNED = 'NOT_RETURNED', 'Not Returned'

    registerId = models.AutoField(primary_key=True)
    reservationId = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name='registers')
    returnedElements = models.JSONField(blank=False, default=dict)
    remainingElements = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name = 'Register'
        verbose_name_plural = 'Registers'
        ordering = ['reservationId']
        indexes = [
            models.Index(fields=['reservation']),
        ]

    def __str__(self):
        return f"{self.registerId}"
