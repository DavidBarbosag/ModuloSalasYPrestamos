from django.db import models
from RecreativeElement.models import RecreativeElement

class Room(models.Model):
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
        recreative_elements (ManyToMany[RecreativeElement]): Recreational elements associated with the reservation.
    """

    id = models.CharField(primary_key=True, max_length=15, blank=False)
    location = models.CharField(max_length=150, blank=False)
    capacity = models.IntegerField(blank=False)
    state = models.CharField(max_length=150, blank=False)
    description = models.TextField(blank=True)

    recreative_elements = models.ManyToManyField(RecreativeElement, through='RoomXElements', related_name='rooms')

    def __str__(self):
        return f"{self.id} en {self.location}"
    

class RoomXElements(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    element = models.ForeignKey(RecreativeElement, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('room', 'element')

    