from rest_framework import serializers
from .models import User
from RecreativeElement.serializers import RecreativeElementSerializer

class UserSerializer(serializers.ModelSerializer):
    recreativeElements = RecreativeElementSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'idNum',
            'name',
            'email',
            'role',
            'profile',
            'recreativeElements',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'user_id': data['id'],
            'identification_number': data['idNum'],
            'full_name': data['name'],
            'email_address': data['email'],
            'role': data['role'],
            'profile': data['profile'],
            'recreative_elements': data['recreativeElements'],
        }

    def to_internal_value(self, data):
        if 'user_id' in data:
            data['id'] = data.pop('user_id')
        if 'identification_number' in data:
            data['idNum'] = data.pop('identification_number')
        if 'full_name' in data:
            data['name'] = data.pop('full_name')
        if 'email_address' in data:
            data['email'] = data.pop('email_address')
        return super().to_internal_value(data)