from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializer import RoomXElementsSerializer, RoomWriteSerializer, RoomReadSerializer
from .models import Room, RoomXElements


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Sala creada exitosamente'}, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return RoomWriteSerializer
        return RoomReadSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='disponibilidad')
    def disponibilidad(self, request, pk=None):
        room = self.get_object()
        return Response({'availability': room.availability})
    
    @action(detail=True, methods=['get'], url_path='elementos')
    def elementos(self, request, pk=None):
        room = self.get_object()
        room_elements = room.roomxelements_set.select_related('element').all()
        
        elementos_data = [{
            'element_id': item.element.id,
            'amount': item.amount,
            'element_details': {
                'id': item.element.id,
                'item_name': item.element.name,
                'item_quantity': item.element.quantity
            }
        } for item in room_elements]
        
        return Response({'elementos': elementos_data})
    
    @action(detail=True, methods=['post'], url_path='add_element')
    def add_element(self, request, pk=None):
        room = self.get_object()
        
        element_id = request.data.get('element_id')
        amount = request.data.get('amount', 1) 
        
        if not element_id:
            return Response(
                {'error': 'Se requiere el ID del elemento (element_id)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            RoomXElements.objects.create(
                room=room,
                element_id=element_id,
                amount=amount
            )
            return Response(
                {'message': 'Elemento agregado correctamente a la sala'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RoomXElementsViewSet(viewsets.ModelViewSet):
    queryset = RoomXElements.objects.all()
    serializer_class = RoomXElementsSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Elemento recreativo agregado a la sala exitosamente'}, 
                       status=status.HTTP_201_CREATED)