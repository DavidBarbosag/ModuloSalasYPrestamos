from rest_framework import serializers
from .models import Room, RoomXElements
from RecreativeElement.models import RecreativeElement

class RoomXElementsSerializer(serializers.ModelSerializer):
    element_id = serializers.PrimaryKeyRelatedField( 
        queryset=RecreativeElement.objects.all(),
        source='element'
    )
    class Meta:
        model = RoomXElements
        fields = ('element_id', 'amount')

class RoomReadSerializer(serializers.ModelSerializer):
    elementos = RoomXElementsSerializer(many=True, source='roomxelements_set')

    class Meta:
        model = Room
        fields = ('id', 'location', 'capacity', 'state', 'description', 'availability', 'elementos')

class RoomWriteSerializer(serializers.ModelSerializer):
    elementos = RoomXElementsSerializer(many=True, write_only=True)

    class Meta:
        model = Room
        fields = ('id', 'location', 'capacity', 'state', 'description', 'availability', 'elementos')

    def create(self, validated_data):
        elementos_data = validated_data.pop('elementos', [])
        room = Room.objects.create(**validated_data)

        for elemento in elementos_data:
            RoomXElements.objects.create(
                room=room,
                element=elemento['element'],
                amount=elemento['amount']
            )
        return room


    def update(self, instance, validated_data):
        elementos_data = validated_data.pop('elementos', None)

        instance.location = validated_data.get('location', instance.location)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.save()

        if elementos_data is not None:
            RoomXElements.objects.filter(room=instance).delete()
            for elemento in elementos_data:
                RoomXElements.objects.create(
                    room=instance,
                    element=elemento['element'],
                    amount=elemento['amount']
                )
        return instance