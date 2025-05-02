from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reservation, ReservationXElements
from .serializer import ReservationSerializer, ReservationCreateSerializer, ReservationXElementsSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        
        # Obtener el serializador de detalle para la respuesta
        response_serializer = ReservationSerializer(reservation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    
class ReservationElementViewSet(viewsets.ModelViewSet):
    queryset = ReservationXElements.objects.all()
    serializer_class = ReservationXElementsSerializer