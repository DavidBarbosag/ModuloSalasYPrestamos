from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializer import RoomSerializer
from .models import Room, RoomXElements


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Sala creada exitosamente'}, status=status.HTTP_201_CREATED)


class RoomXElementsViewSet(viewsets.ModelViewSet):
    queryset = RoomXElements.objects.all()
    serializer_class = RoomSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Elemento recreativo agregado a la sala exitosamente'}, 
                       status=status.HTTP_201_CREATED)