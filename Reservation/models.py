from django.db import models
from RecreativeElement.models import RecreativeElement
from Room.models import Room
from django.contrib.auth import get_user_model
User = get_user_model() 
from django.conf import settings

class Reservation(models.Model):
    """
    Represents a reservation for a recreational element.

    Attributes:
        id (str): Unique identifier for the reservation (used as the primary key).
        start_time (datetime): Start time of the reservation.
        room (str): Room associated with the reservation.
        location (str): Location of the reservation.
        state (str): State of the reservation.
        user (User): User who made the reservation (foreign key to User model).
        register (Register): Register associated with the reservation (foreign key to Register model).
        borrowed_elements (ManyToMany[RecreativeElement]): Recreational elements associated with the reservation.
        reserved_day (str): Day of the week for the reservation (e.g., "Lunes").
        reserved_hour_block (str): Hour block for the reservation (e.g., "7:00-8:30").
    """

    id = models.AutoField(primary_key=True, blank=False)

    reserved_day = models.CharField(max_length=20, blank=True, null=True)
    reserved_hour_block = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=150, blank=False)
    state = models.CharField(max_length=150, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', blank=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room', blank=True, null=True)
    register = models.ForeignKey("Register.Register", on_delete=models.PROTECT, related_name='reservations', blank=True, null=True)
    borrowed_elements = models.ManyToManyField(RecreativeElement, through='ReservationXElements', related_name='reservations', blank=True)

    def __str__(self):
            return f"{self.id} - {self.user.id}"

    def save(self, *args, **kwargs):
        """
        Override save method to initialize reserved_day and reserved_hour_block
        if they are not set yet.
        """
        super().save(*args, **kwargs)

class ReservationXElements(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    element = models.ForeignKey(RecreativeElement, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('reservation', 'element')