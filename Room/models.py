from django.db import models
from Exceptions.customException import exception, customException
from RecreativeElement.models import RecreativeElement

def defaultAvailability():
    return [[0] * 6 for _ in range(8)]

class Room(models.Model):
    """
    Representa una sala con elementos recreativos.

    Atributos:
        id (str): Identificador único de la sala (clave primaria).
        location (str): Ubicación de la sala.
        capacity (int): Capacidad máxima de la sala.
        state (str): Estado actual de la sala.
        description (str): Descripción opcional de la sala.
        availability (list): Disponibilidad de la sala en horarios y días.
        recreative_elements (ManyToMany[RecreativeElement]): Elementos recreativos asociados.
    """

    id = models.AutoField(primary_key=True, blank=False)
    location = models.CharField(max_length=150, blank=False)
    capacity = models.IntegerField(blank=False)
    state = models.CharField(max_length=150, blank=False)
    description = models.TextField(blank=True)
    availability = models.JSONField(default=defaultAvailability, blank=False, null=False)
    recreative_elements = models.ManyToManyField(RecreativeElement, through='RoomXElements', related_name='rooms')

    # Diccionario para mapear horarios a índices
    HOURS = {
        "7:00-8:30": 0,
        "8:30-10:00": 1,
        "10:00-11:30": 2,
        "11:30-13:00": 3,
        "13:00-14:30": 4,
        "14:30-16:00": 5,
        "16:00-17:30": 6,
        "17:30-19:00": 7
    }

    # Diccionario para mapear días a índices
    DAYS = {
        "Lunes": 0,
        "Martes": 1,
        "Miércoles": 2,
        "Jueves": 3,
        "Viernes": 4,
        "Sabado": 5
    }

    def clean(self):
        """
        Check the attributes.

        Raises:
            ValidationError: if the availability format is invalid.
        """
        super().clean()
        if not isinstance(self.availability, list) or len(self.availability) != 8 or len(self.availability[0]) != 6:
            raise customException(exception.INVALID_ROOMAVAILABILITY)

    def reserveRoom(self, day, hour):
        """
        Reserve a room in a specified time.

        Args:
            day (str): week day.
            hour (str): hour.

        Raises:
            ValidationError: Si la sala ya está reservada en ese horario.
        """
        if self.availability[self.DAYS[day]][self.HOURS[hour]] == 1:
            raise customException(exception.ROOMALREADY_RESERVED)
        self.availability[self.DAYS[day]][self.HOURS[hour]] = 1
        self.save(update_fields=['availability'])

    def __str__(self):
        return f"{self.id} en {self.location}"


class RoomXElements(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    element = models.ForeignKey(RecreativeElement, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('room', 'element')

