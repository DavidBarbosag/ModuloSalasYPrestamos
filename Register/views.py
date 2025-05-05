from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Register
from .serializers import RegisterSerializer

class RegisterView(APIView):
    def get(self, request, identifier=None):
        """
        Get all registers or a specific register by id.
        """
        if identifier:
            return self.getRegisterById(request, identifier)
        registers = Register.objects.all()
        serializer = RegisterSerializer(registers, many=True)
        return Response(serializer.data)

    def getRegisterById(self, request, identifier):
        """
        Get a register by id.
        """
        try:
            register = Register.objects.filter(registerId=identifier).first()
            if not register:
                return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = RegisterSerializer(register)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Create a new register.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, identifier):
        """
        Delete a register.
        """
        try:
            register = Register.objects.filter(registerId=identifier).first()
            if not register:
                return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            register.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, identifier):
        """
        Update a register.
        """
        try:
            register = Register.objects.filter(registerId=identifier).first()
            if not register:
                return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = RegisterSerializer(register, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, identifier):
        """
        Partial update.
        """
        try:
            register = Register.objects.filter(registerId=identifier).first()
            if not register:
                return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = RegisterSerializer(register, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)