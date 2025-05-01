from rest_framework import serializers
from .models import Register

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['registerId', 'reservationId', 'returnedElements', 'remainingElements']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'register_id': data['registerId'],
            'reservation_id': data['reservationId'],
            'returned_elements': data['returnedElements'],
            'remaining_elements': data['remainingElements'],
        }
    def to_internal_value(self, data):
        if 'register_id' in data:
            data['registerId'] = data.pop('register_id')
        if 'reservation_id' in data:
            data['reservationId'] = data.pop('reservation_id')
        if 'returned_elements' in data:
            data['returnedElements'] = data.pop('returned_elements')
        if 'remaining_elements' in data:
            data['remainingElements'] = data.pop('remaining_elements')
        return super().to_internal_value(data)