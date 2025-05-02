from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import RoomSerializer
from .models import Room, RoomXElements


class Room(APIView):
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Sala creada exitosamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RoomXElements(APIView):
    def get(self, request):
        room_elements = RoomXElements.objects.all()
        serializer = RoomSerializer(room_elements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):    
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Elemento recreativo agregado a la sala exitosamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    