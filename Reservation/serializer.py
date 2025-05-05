from rest_framework import serializers
from .models import Reservation, ReservationXElements
from RecreativeElement.serializers import RecreativeElementSerializer
from Room.serializer import RoomSerializer
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
    room_details = RoomSerializer(source='room', read_only=True)
    borrowed_elements = ReservationXElementsSerializer(source='reservationxelements_set', many=True, read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'start_time', 'location', 'state', 
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
        required=False, write_only=True
    )
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'start_time', 'location', 'state', 
            'user', 'room', 'register', 'borrowed_elements'
        ]
    
    def create(self, validated_data):
        borrowed_elements_data = validated_data.pop('borrowed_elements', [])
        reservation = Reservation.objects.create(**validated_data)
        
        for element_data in borrowed_elements_data:
            element_id = element_data.get('element')
            amount = element_data.get('amount', 1)
            if element_id:
                ReservationXElements.objects.create(
                    reservation=reservation,
                    element_id=element_id,
                    amount=amount
                )
        
        return reservation