from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reservation, ReservationXElements
from .serializer import ReservationSerializer, ReservationCreateSerializer, ReservationXElementsSerializer
from Room.models import Room
from datetime import datetime, timedelta
from django.utils import timezone
from Exceptions.customException import exception, customException
from django.db import transaction
import calendar
from django.db.models import Q

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

        # Validar que la nueva sala no esté ocupada (excepto por esta reserva)
        if not new_room.is_available(new_day, new_hour_block):
            return Response(
                {"detail": "El nuevo horario ya está reservado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar bloque horario
        valid_blocks = list(new_room.HOURS.keys())
        if new_hour_block not in valid_blocks:
            return Response(
                {"detail": "El nuevo bloque horario no es válido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar día de la semana
        valid_days = list(new_room.DAYS.keys())
        if new_day not in valid_days:
            return Response(
                {"detail": "El nuevo día de la reserva no es válido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Liberar la reserva anterior
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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room_id = serializer.validated_data.get('room')
        reserved_day = serializer.validated_data.get('reserved_day')
        reserved_hour_block = serializer.validated_data.get('reserved_hour_block')

        if room_id and reserved_day and reserved_hour_block:
            result = self._validate_new_reservation(room_id.id, reserved_day, reserved_hour_block)
            if isinstance(result, Response):
                return result

        reservation = serializer.save()
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

        if room_id and reserved_day and reserved_hour_block:
            result = self._validate_update_reservation(
                reservation,
                room_id.id,
                reserved_day,
                reserved_hour_block
            )
            if isinstance(result, Response):
                return result

        updated_reservation = serializer.save()
        response_serializer = ReservationSerializer(updated_reservation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        
        if reservation.room and reservation.reserved_day and reservation.reserved_hour_block:
            room = reservation.room
            try:
                # Liberar el horario específico
                room.releaseRoom(reservation.reserved_day, reservation.reserved_hour_block)
   
            except customException as e:
                return Response(
                    {"detail": f"Error al liberar la sala: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Eliminar la reserva
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def search(self, request):
        search_param = request.query_params.get('q', '').strip()

        if not search_param:
            return Response({'error': 'Parámetro de búsqueda vacío'}, status=status.HTTP_400_BAD_REQUEST)

        if search_param.isdigit():
            reservations = self.queryset.filter(id=int(search_param))
        else:
            reservations = self.queryset.none()

        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)
    
class ReservationElementViewSet(viewsets.ModelViewSet):
    queryset = ReservationXElements.objects.all()
    serializer_class = ReservationXElementsSerializer


