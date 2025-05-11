from django.db import models
from Exceptions.customException import exception, customException
from RecreativeElement.models import RecreativeElement

def defaultAvailability():
    return [[0] * 6 for _ in range(8)]

class Room(models.Model):
    """
    Represents a room with recreative elements.

    Attributes:
        id (str): Unique identifier of the room (primary key).
        location (str): Room location.
        capacity (int): Maximum capacity of the room.
        description (str): Optional description of the room.
        availability (list): Room availability by schedules and days.
        recreative_elements (ManyToMany[RecreativeElement]): Associated recreational elements.
    """

    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=150, blank=False)
    capacity = models.IntegerField(blank=False)
    description = models.TextField(blank=True)
    availability = models.JSONField(default=defaultAvailability, blank=False, null=False)
    recreative_elements = models.ManyToManyField(RecreativeElement, through='RoomXElements', related_name='rooms')

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
            exception.raise_invalid_room_availability()

    def reserveRoom(self, day, hour):
        """
        Reserva la sala en un horario específico.

        Args:
            day (str): Día de la semana (ej. "Lunes")
            hour (str): Bloque horario (ej. "10:00-11:30")

        Returns:
            bool: True si se reservó correctamente

        Raises:
            customException: Si la sala ya está reservada en ese horario
        """
        day_index = self.DAYS.get(day)
        hour_index = self.HOURS.get(hour)
        
        if day_index is None or hour_index is None:
            raise customException(exception.INVALID_DAYHOUR)
            
        if self.availability[hour_index][day_index] == 1:
            return False
            
        self.availability[hour_index][day_index] = 1
        self.save(update_fields=['availability'])
        
        return True

    def releaseRoom(self, day, hour):
        """
        Libera una sala previamente reservada en un horario específico.

        Args:
            day (str): Día de la semana (ej. "Lunes")
            hour (str): Bloque horario (ej. "10:00-11:30")

        Returns:
            bool: True si se liberó correctamente

        Raises:
            customException: Si el día u horario no son válidos
        """
        day_index = self.DAYS.get(day)
        hour_index = self.HOURS.get(hour)
        
        if day_index is None or hour_index is None:
            raise customException(exception.INVALID_DAYHOUR)
            
        if self.availability[hour_index][day_index] == 0:
            return False
            
        self.availability[hour_index][day_index] = 0
        self.save(update_fields=['availability'])
        return True
        
    def checkIfRoomIsFullyBooked(self):
        """
        Verifica si la sala está completamente reservada para actualizar su estado.
        
        Returns:
            bool: True si la sala está completamente reservada, False en caso contrario.
        """
        for hour_row in self.availability:
            for day_cell in hour_row:
                if day_cell == 0:
                    return False
        return True
    
    def is_available(self, day, hour):
        """Verifica si la sala está disponible en un horario específico"""
        day_index = self.DAYS.get(day)
        hour_index = self.HOURS.get(hour)
        
        if day_index is None or hour_index is None:
            raise customException(exception.INVALID_DAYHOUR)
            
        return self.availability[hour_index][day_index] == 0

    def getRoomAvailability(self, roomId):
        """
        Get the availability of a room.

        Args:
            roomId (int): Room ID.

        Returns:
            list: Availability of the room.
        """
        try:
            room = Room.objects.get(id=roomId)
            return room.availability
        except Room.DoesNotExist:
            exception.raise_room_not_found()

    def getRecrereativeElements(self, roomId):
        """
        Get the recreative elements of a room.

        Args:
            roomId (int): Room ID.

        Returns:
            list: List of recreative elements as JSON.
        """
        try:
            room = Room.objects.get(id=roomId)
            recreativeElements = room.recreative_elements.all()
            elements_json = [
                {"name": element.name, "quantity": element.quantity}
                for element in recreativeElements
            ]
            return elements_json
        except Room.DoesNotExist:
            exception.raise_room_not_found()


    def __str__(self):
        return f"{self.id} - {self.location}"



class RoomXElements(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    element = models.ForeignKey(RecreativeElement, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('room', 'element')
