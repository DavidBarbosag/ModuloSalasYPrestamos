from rest_framework import serializers
from .models import Reservation, ReservationXElements
from Room.models import RoomXElements
from RecreativeElement.serializers import RecreativeElementSerializer
from Room.serializer import RoomReadSerializer
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ReservationXElementsSerializer(serializers.ModelSerializer):
    element_details = RecreativeElementSerializer(source='element', read_only=True)
    
    class Meta:
        model = ReservationXElements
        fields = ['element', 'amount', 'element_details']


class ReservationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    room_details = RoomReadSerializer(source='room', read_only=True)
    borrowed_elements = ReservationXElementsSerializer(source='reservationxelements_set', many=True, read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'location', 'state',
            'reserved_day', 'reserved_hour_block',
            'user', 'user_details',
            'room', 'room_details',
            'register', 
            'borrowed_elements'
        ]
        read_only_fields = ['user_details', 'room_details', 'borrowed_elements']



class ReservationCreateSerializer(serializers.ModelSerializer):
    borrowed_elements = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        ),
        required=False, 
        write_only=True,
        default=[]
    )
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'location', 'state',
            'reserved_day', 'reserved_hour_block',
            'user', 'room', 'register', 'borrowed_elements'
        ]
    
    def validate_borrowed_elements(self, value):
        """Validación personalizada para los elementos prestados"""
        for element_data in value:
            if not any(key in element_data for key in ['element', 'element_id']):
                raise serializers.ValidationError(
                    "Cada elemento debe incluir 'element' o 'element_id'"
                )
            if 'amount' not in element_data or element_data['amount'] <= 0:
                raise serializers.ValidationError(
                    "Cada elemento debe incluir una 'amount' válida (mayor que 0)"
                )
        return value
    
    def validate(self, data):
        """Validación adicional antes de la creación"""
        room = data.get('room')
        borrowed_elements = data.get('borrowed_elements', [])
        
        if room and borrowed_elements:
            # Verificar que todos los elementos pertenecen a la sala
            room_element_ids = set(
                RoomXElements.objects.filter(room=room)
                .values_list('element_id', flat=True)
            )
            
            for element_data in borrowed_elements:
                element_id = element_data.get('element') or element_data.get('element_id')
                amount = element_data.get('amount', 1)
                
                if element_id not in room_element_ids:
                    raise serializers.ValidationError(
                        f"El elemento con ID {element_id} no está disponible en la sala {room.id}"
                    )
                
                # Verificar disponibilidad
                try:
                    room_element = RoomXElements.objects.get(
                        room=room,
                        element_id=element_id
                    )
                    if room_element.amount < amount:
                        raise serializers.ValidationError(
                            f"No hay suficientes unidades disponibles del elemento {element_id}. "
                            f"Disponibles: {room_element.amount}, Solicitadas: {amount}"
                        )
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        f"El elemento con ID {element_id} no está disponible en la sala {room.id}"
                    )
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Creación de la reserva con manejo de elementos"""
        borrowed_elements_data = validated_data.pop('borrowed_elements', [])
        room = validated_data.get('room')
        
        # Crear la reserva base
        reservation = Reservation.objects.create(**validated_data)
        
        # Procesar elementos si existen y hay sala asignada
        if borrowed_elements_data and room:
            self._process_elements(reservation, borrowed_elements_data)
        
        return reservation
    
    def _process_elements(self, reservation, elements_data):
        """Procesa los elementos recreativos y actualiza inventarios"""
        for element_data in elements_data:
            element_id = element_data.get('element') or element_data.get('element_id')
            amount = element_data.get('amount', 1)
            
            # Crear relación en ReservationXElements
            ReservationXElements.objects.create(
                reservation=reservation,
                element_id=element_id,
                amount=amount
            )
            
            # Actualizar cantidad en RoomXElements
            room_element = RoomXElements.objects.get(
                room=reservation.room,
                element_id=element_id
            )
            room_element.amount -= amount
            room_element.save()
