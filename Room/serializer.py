from rest_framework import serializers
from .models import Room, RoomXElements
from RecreativeElement.models import RecreativeElement

class RoomXElementsSerializer(serializers.ModelSerializer):
    element_id = serializers.PrimaryKeyRelatedField(
        queryset=RecreativeElement.objects.all(),
        source='element'
    )
    element_details = serializers.SerializerMethodField()

    class Meta:
        model = RoomXElements
        fields = ('element_id', 'amount', 'element_details')

    def get_element_details(self, obj):
        return {
            'id': obj.element.id,
            'item_name': obj.element.item_name,
            'item_quantity': obj.element.item_quantity
        }

class RoomReadSerializer(serializers.ModelSerializer):
    elementos = serializers.SerializerMethodField()
    
    def get_elementos(self, obj):
        elements = obj.roomxelements_set.select_related('element').all()
        return [{
            'element_id': item.element.id,
            'amount': item.amount,
            'element_details': {
                'id': item.element.id,
                'item_name': item.element.name,
                'item_quantity': item.element.quantity
            }
        } for item in elements]

    class Meta:
        model = Room
        fields = ('id', 'location', 'capacity', 'description', 'availability', 'elementos')
        read_only_fields = fields

class RoomWriteSerializer(serializers.ModelSerializer):
    elementos = RoomXElementsSerializer(many=True, required=False)

    class Meta:
        model = Room
        fields = ('id', 'location', 'capacity', 'description', 'availability', 'elementos')
        extra_kwargs = {
            'location': {'required': False},
            'description': {'required': False},
            'availability': {'required': False},
            'capacity': {'required': False}
        }

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
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if validated_data:
            instance.save()

        if elementos_data is not None:
            self._update_elements(instance, elementos_data)

        instance.refresh_from_db()
        return instance

    def _update_elements(self, room, elementos_data):
        """Método helper para actualizar elementos recreativos"""
        current_elements = {elem.element_id: elem for elem in room.roomxelements_set.all()}
        
        for elemento in elementos_data:
            element_id = elemento['element'].id
            if element_id in current_elements:

                current_elements[element_id].amount = elemento['amount']
                current_elements[element_id].save()
            else:

                RoomXElements.objects.create(
                    room=room,
                    element=elemento['element'],
                    amount=elemento['amount']
                )
        
        received_ids = {elem['element'].id for elem in elementos_data}
        for element_id, element in current_elements.items():
            if element_id not in received_ids:
                element.delete()