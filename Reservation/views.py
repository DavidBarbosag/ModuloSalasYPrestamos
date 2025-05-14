from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reservation, ReservationXElements
from .serializer import ReservationSerializer, ReservationCreateSerializer, ReservationXElementsSerializer
from Room.models import Room, RoomXElements
from Exceptions.customException import exception, customException
from django.db import transaction

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def _validate_new_reservation(self, room_id, reserved_day, reserved_hour_block):
        """
        Validar una nueva reserva de sala (solo para creación)
        
        Args:
            room_id: ID de la sala a reservar
            reserved_day: Día de la semana (en español)
            reserved_hour_block: Bloque horario (e.g., "7:00-8:30")
            
        Returns:
            room: Objeto Room si la validación es exitosa
            
        Raises:
            Response: Respuesta HTTP con error si hay problemas
        """
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"detail": "La sala no existe"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not room.is_available(reserved_day, reserved_hour_block):
            return Response(
                {"detail": "El horario seleccionado ya está reservado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar bloque horario
        valid_blocks = list(room.HOURS.keys())
        if reserved_hour_block not in valid_blocks:
            return Response(
                {"detail": "El bloque horario no es válido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar día de la semana
        valid_days = list(room.DAYS.keys())
        if reserved_day not in valid_days:
            return Response(
                {"detail": "El día de la reserva no es válido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Intentar reservar
        try:
            room.reserveRoom(reserved_day, reserved_hour_block)
            room.save()
        except customException as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return room

    def _validate_update_reservation(self, reservation, new_room_id, new_day, new_hour_block):
        """
        Validar actualización de una reserva existente
        
        Args:
            reservation: Objeto Reservation a actualizar
            new_room_id: Nuevo ID de sala (puede ser el mismo)
            new_day: Nuevo día (puede ser el mismo)
            new_hour_block: Nuevo bloque horario (puede ser el mismo)
            
        Returns:
            tuple: (room, new_day, new_hour_block) si la validación es exitosa
            
        Raises:
            Response: Respuesta HTTP con error si hay problemas
        """
        try:
            new_room = Room.objects.get(id=new_room_id)
        except Room.DoesNotExist:
            return Response({"detail": "La nueva sala no existe"}, status=status.HTTP_400_BAD_REQUEST)

        # Solo validar disponibilidad si es un horario diferente al actual
        current_slot = (reservation.reserved_day, reservation.reserved_hour_block)
        new_slot = (new_day, new_hour_block)
        
        if new_slot != current_slot:
            if not new_room.is_available(new_day, new_hour_block):
                return Response(
                    {"detail": f"El horario {new_hour_block} del día {new_day} ya está reservado"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validar bloque horario
        valid_blocks = list(new_room.HOURS.keys())
        if new_hour_block not in valid_blocks:
            return Response(
                {"detail": f"El bloque horario no es válido. Bloques válidos: {', '.join(valid_blocks)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar día de la semana
        valid_days = list(new_room.DAYS.keys())
        if new_day not in valid_days:
            return Response(
                {"detail": f"El día de la reserva no es válido. Días válidos: {', '.join(valid_days)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Liberar la reserva anterior (solo si el horario cambió)
        if new_slot != current_slot:
            try:
                reservation.room.releaseRoom(reservation.reserved_day, reservation.reserved_hour_block)
                reservation.room.save()
            except customException as e:
                return Response({"detail": f"Error al liberar la reserva anterior: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

            # Reservar la nueva configuración
            try:
                new_room.reserveRoom(new_day, new_hour_block)
                new_room.save()
            except customException as e:
                # Revertir la liberación si falla la nueva reserva
                try:
                    reservation.room.reserveRoom(reservation.reserved_day, reservation.reserved_hour_block)
                    reservation.room.save()
                except Exception:
                    pass
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return new_room, new_day, new_hour_block

    def _validate_elements(self, room, elements_data):
        """Valida que los elementos existan en la sala y haya suficiente cantidad"""
        room_elements = {re.element.id: re.amount for re in RoomXElements.objects.filter(room=room)}
        
        for element_data in elements_data:
            element_id = element_data.get('element') or element_data.get('element_id')
            amount = element_data.get('amount', 1)
            
            if element_id not in room_elements:
                raise Exception(f"El elemento con ID {element_id} no está disponible en la sala {room.id}")
            
            if amount > room_elements[element_id]:
                raise Exception(f"No hay suficientes unidades disponibles del elemento {element_id}. Disponibles: {room_elements[element_id]}, Solicitadas: {amount}")

    def _process_elements(self, reservation, elements_data):
        """Crea las relaciones y actualiza cantidades"""
        for element_data in elements_data:
            element_id = element_data.get('element') or element_data.get('element_id')
            amount = element_data.get('amount', 1)
            
            # Crear relación
            ReservationXElements.objects.create(
                reservation=reservation,
                element_id=element_id,
                amount=amount
            )
            
            # Actualizar cantidad en sala
            room_element = RoomXElements.objects.get(room=reservation.room, element_id=element_id)
            room_element.amount -= amount
            room_element.save()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room_id = serializer.validated_data.get('room')
        reserved_day = serializer.validated_data.get('reserved_day')
        reserved_hour_block = serializer.validated_data.get('reserved_hour_block')
        elements_data = request.data.get('borrowed_elements', [])

        # Validar sala y horario
        if room_id and reserved_day and reserved_hour_block:
            result = self._validate_new_reservation(room_id.id, reserved_day, reserved_hour_block)
            if isinstance(result, Response):
                return result

        # Validar elementos si se proporcionan
        if elements_data:
            try:
                room = Room.objects.get(id=room_id.id)
                self._validate_elements(room, elements_data)
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear reserva
        reservation = serializer.save()
        
        # Procesar elementos
        if elements_data:
            try:
                self._process_elements(reservation, elements_data)
            except Exception as e:
                return Response(
                    {"detail": f"Error al procesar elementos: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        response_serializer = ReservationSerializer(reservation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        room_id = serializer.validated_data.get('room', reservation.room)
        reserved_day = serializer.validated_data.get('reserved_day', reservation.reserved_day)
        reserved_hour_block = serializer.validated_data.get('reserved_hour_block', reservation.reserved_hour_block)
        elements_data = request.data.get('borrowed_elements', None)

        # Validar sala y horario
        if room_id and reserved_day and reserved_hour_block:
            result = self._validate_update_reservation(
                reservation,
                room_id.id,
                reserved_day,
                reserved_hour_block
            )
            if isinstance(result, Response):
                return result

        # Si se están actualizando los elementos
        if elements_data is not None:
            # Primero, revertir las cantidades de los elementos anteriores
            for element_relation in reservation.reservationxelements_set.all():
                try:
                    room_element = RoomXElements.objects.get(
                        room=reservation.room,
                        element=element_relation.element
                    )
                    room_element.amount += element_relation.amount
                    room_element.save()
                except RoomXElements.DoesNotExist:
                    pass
            
            # Eliminar relaciones anteriores
            reservation.reservationxelements_set.all().delete()
            
            # Validar y procesar nuevos elementos
            try:
                room = Room.objects.get(id=room_id.id)
                self._validate_elements(room, elements_data)
                self._process_elements(reservation, elements_data)
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        updated_reservation = serializer.save()
        response_serializer = ReservationSerializer(updated_reservation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        
        # Devolver elementos a la sala
        for element_relation in reservation.reservationxelements_set.all():
            try:
                room_element = RoomXElements.objects.get(
                    room=reservation.room,
                    element=element_relation.element
                )
                room_element.amount += element_relation.amount
                room_element.save()
            except RoomXElements.DoesNotExist:
                RoomXElements.objects.create(
                    room=reservation.room,
                    element=element_relation.element,
                    amount=element_relation.amount
                )
        
        # Liberar horario
        if reservation.room and reservation.reserved_day and reservation.reserved_hour_block:
            try:
                reservation.room.releaseRoom(reservation.reserved_day, reservation.reserved_hour_block)
                reservation.room.save()
            except customException as e:
                return Response(
                    {"detail": f"Error al liberar la sala: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().destroy(request, *args, **kwargs)

    # En ReservationViewSet.finalize_reservation
    @action(detail=True, methods=['post'], url_path='finalize')
    @transaction.atomic
    def finalize_reservation(self, request, pk=None):
        reservation = self.get_object()
        
        # Validación de estado
        if reservation.state == 'FINALIZADA':
            return Response(
                {"detail": "La reserva ya está finalizada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de payload
        returned_elements = request.data.get('returned_elements', [])
        if not returned_elements:
            return Response(
                {"detail": "Se requiere al menos un elemento devuelto"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validación de elementos únicos
        element_ids = [e['element_id'] for e in returned_elements]
        if len(element_ids) != len(set(element_ids)):
            return Response(
                {"detail": "Elementos duplicados en la lista de devolución"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validación de estructura
        for element in returned_elements:
            if not all(key in element for key in ['element_id', 'amount', 'status']):
                return Response(
                    {"detail": "Cada elemento debe tener element_id, amount y status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if element['status'] not in ['RETURNED_GOOD', 'RETURNED_DAMAGED', 'NOT_RETURNED']:
                return Response(
                    {"detail": "Estado inválido. Use RETURNED_GOOD, RETURNED_DAMAGED o NOT_RETURNED"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validación de cantidades
        try:
            original_elements = ReservationXElements.objects.filter(reservation=reservation)
            original_amounts = {elem.element_id: elem.amount for elem in original_elements}
            
            returned_amounts = {}
            for element in returned_elements:
                element_id = element['element_id']
                returned_amounts[element_id] = returned_amounts.get(element_id, 0) + element['amount']
            
            # Verificar coincidencia de cantidades
            for element_id, original_amount in original_amounts.items():
                returned_amount = returned_amounts.get(element_id, 0)
                if returned_amount != original_amount:
                    return Response(
                        {"detail": f"Cantidad incorrecta para el elemento {element_id}. Esperado: {original_amount}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Verificar que todos los elementos de la reserva están incluidos
            for element_id in original_amounts.keys():
                if element_id not in returned_amounts:
                    return Response(
                        {"detail": f"Falta el elemento {element_id} en la devolución"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except Exception as e:
            return Response(
                {"detail": f"Error en validación de cantidades: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Procesar devolución
        try:
            reservation.finalize_reservation(
                returned_elements=returned_elements,
                admin_comment=request.data.get('admin_comment')
            )
            return Response(
                {"detail": "Reserva finalizada correctamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al finalizar reserva: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class ReservationElementViewSet(viewsets.ModelViewSet):
    queryset = ReservationXElements.objects.all()
    serializer_class = ReservationXElementsSerializer