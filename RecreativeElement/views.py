from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RecreativeElement
from .serializers import RecreativeElementSerializer


class RecreativeElementView(APIView):
    def get(self, request):
        elements = RecreativeElement.objects.all()
        serializer = RecreativeElementSerializer(elements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecreativeElementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)