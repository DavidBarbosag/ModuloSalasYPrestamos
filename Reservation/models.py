from django.db import models
from RecreativeElement.models import RecreativeElement
from Room.models import Room
from django.contrib.auth import get_user_model
User = get_user_model() 
from django.conf import settings
from django.db import transaction
from Room.models import RoomXElements
import logging

logger = logging.getLogger(__name__)
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


    def finalize_reservation(self, returned_elements, admin_comment=None):
        """
        Finaliza una reserva, devuelve los elementos y registra el estado
        
        Args:
            returned_elements: Lista de elementos devueltos con su estado
                Ejemplo: [{
                    'element_id': 1,
                    'amount': 2,
                    'status': 'RETURNED_GOOD' | 'RETURNED_DAMAGED' | 'NOT_RETURNED'
                }]
            admin_comment: Comentario opcional del administrador
        """
        with transaction.atomic():
            # 1. Devolver elementos a la sala
            self._return_elements_to_room(returned_elements)
            
            # 2. Liberar el horario de la sala
            if self.room and self.reserved_day and self.reserved_hour_block:
                self.room.releaseRoom(self.reserved_day, self.reserved_hour_block)
                self.room.save()
            
            # 3. Crear registro de devolución
            self._create_return_register(returned_elements, admin_comment)
            
            # 4. Actualizar estado de la reserva
            self.state = 'FINALIZADA'
            self.save()
    
    def _return_elements_to_room(self, returned_elements):
        """Devuelve los elementos a la sala y actualiza cantidades"""
        for element_data in returned_elements:
            element_id = element_data['element_id']
            returned_amount = element_data['amount']
            
            try:
                # Obtener relación de préstamo
                reservation_element = ReservationXElements.objects.get(
                    reservation=self,
                    element_id=element_id
                )
                
                # Solo devolver elementos si el estado no es NOT_RETURNED
                if element_data['status'] != 'NOT_RETURNED':
                    # Actualizar cantidad en la sala
                    room_element = RoomXElements.objects.get(
                        room=self.room,
                        element_id=element_id
                    )
                    room_element.amount += returned_amount
                    room_element.save()
                
                # Eliminar la relación de préstamo
                reservation_element.delete()
                
            except (ReservationXElements.DoesNotExist, RoomXElements.DoesNotExist) as e:
                # Registrar error pero continuar con otros elementos
                logger.error(f"Error al devolver elemento {element_id}: {str(e)}")
                continue
    
    def _create_return_register(self, returned_elements, admin_comment):
        """Crea el registro de devolución en el modelo Register"""
        from Register.models import Register
        
        # Preparar datos para el registro
        returned_elements_data = []
        remaining_elements_data = []
        
        for element_data in returned_elements:
            element = RecreativeElement.objects.get(id=element_data['element_id'])
            element_info = {
                'codigo': element.id,
                'nombre': element.name,
                'estado': element_data['status'],
                'cantidad': element_data['amount']
            }
            
            if element_data['status'] == 'NOT_RETURNED':
                remaining_elements_data.append(element_info)
            else:
                returned_elements_data.append(element_info)
        
        # Crear registro
        Register.objects.create(
            reservationId=self,
            returnedElements={'elements': returned_elements_data},
            remainingElements={'elements': remaining_elements_data},
            admin_comment=admin_comment
        )
class ReservationXElements(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    element = models.ForeignKey(RecreativeElement, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('reservation', 'element')