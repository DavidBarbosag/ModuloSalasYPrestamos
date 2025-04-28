from rest_framework import serializers
from .models import Room, RoomXElements
from RecreativeElement.models import RecreativeElement

class RoomXElementsSerializer(serializers.ModelSerializer):
    element_id = serializers.CharField(write_only=True)
    class Meta:
        model = RoomXElements
        fields = ('element_id', 'amount')

class RoomSerializer(serializers.ModelSerializer):
    elementos = RoomXElementsSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Room
        fields = ('id', 'location', 'capacity', 'state', 'description', 'elementos')

    def create(self, validated_data):
        elementos_data = validated_data.pop('elementos', [])
        room = Room.objects.create(**validated_data)

        for elemento in elementos_data:
            element = RecreativeElement.objects.get(id=elemento['element_id'])
            RoomXElements.objects.create(
                room=room,
                element=element,
                amount=elemento['amount']
            )

        return room
