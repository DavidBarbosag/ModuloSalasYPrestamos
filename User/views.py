from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class UserView(APIView):
    def get(self, request, identifier=None):
        """
        Get Users by id or name or get all Users.
        """
        if identifier:
            return self.getUserByIdOrName(request, identifier)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def getUserByIdOrName(self, request, identifier):
        """
        Get Users by id or name.
        """
        try:
            user = User.objects.filter(id=identifier).first() or \
                   User.objects.filter(name=identifier).first()
            if not user:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)