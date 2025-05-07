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

    @action(detail=True, methods=['get'], url_path='disponibilidad')
    def disponibilidad(self, request, pk=None):
        room = self.get_object()
        return Response({'availability': room.availability})
    
    @action(detail=True, methods=['get'], url_path='elementos')
    def elementos(self, request, pk=None):
        room = self.get_object()
        return Response({'elementos': room.recreative_elements.all()})

class RoomXElementsViewSet(viewsets.ModelViewSet):
    queryset = RoomXElements.objects.all()
    serializer_class = RoomXElementsSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Elemento recreativo agregado a la sala exitosamente'}, 
                       status=status.HTTP_201_CREATED)