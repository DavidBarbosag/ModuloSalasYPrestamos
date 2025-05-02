from rest_framework import serializers
from .models import RecreativeElement

class RecreativeElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecreativeElement
        fields = ['id', 'name', 'quantity']

    def to_representation(self, instance):
        """Transforma los nombres de campos al enviar la respuesta"""
        data = super().to_representation(instance)

        return {
            'id': data['id'],
            'item_name': data['name'],
            'item_quantity': data['quantity']
        }

    def to_internal_value(self, data):
        """Transforma los nombres de campos al recibir datos"""

        if 'item_name' in data:
            data['name'] = data.pop('item_name')
        if 'item_quantity' in data:
            data['quantity'] = data.pop('item_quantity')
        return super().to_internal_value(data)