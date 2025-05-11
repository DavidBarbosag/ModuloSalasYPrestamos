from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RecreativeElement
from .serializers import RecreativeElementSerializer


class RecreativeElementView(APIView):
    def get(self, request, identifier=None):
        """
        Get all elements or a specific element by id or name.
        """
        if identifier:
            return self.getRecreativeElementByIdOrName(request, identifier)
        elements = RecreativeElement.objects.all()
        serializer = RecreativeElementSerializer(elements, many=True)
        return Response(serializer.data)

    def getRecreativeElementByIdOrName(self, request, identifier):
        """
        Get an element by id or name.
        """
        try:
            element = RecreativeElement.objects.filter(id=identifier).first() or \
                      RecreativeElement.objects.filter(name=identifier).first()
            if not element:
                return Response({"error": "RecreativeElement no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = RecreativeElementSerializer(element)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = RecreativeElementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, identifier):
        """
        Delete an element.
        """
        try:
            element = RecreativeElement.objects.filter(id=identifier).first() or \
                      RecreativeElement.objects.filter(name=identifier).first()
            if not element:
                return Response({"error": "RecreativeElement no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            element.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, identifier):
        """
        Update.
        """

        try:
            element = RecreativeElement.objects.filter(id=identifier).first() or \
                      RecreativeElement.objects.filter(name=identifier).first()
            if not element:
                return Response({"error": "RecreativeElement no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            serializer = RecreativeElementSerializer(element, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, identifier=None):
        """
        Partial update.
        """
        if not identifier:
            return Response(
                {"error": "Se requiere un identificador (ID o nombre) para actualizar"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            try:
                element = RecreativeElement.objects.get(id=identifier)
            except (RecreativeElement.DoesNotExist, ValueError):
                # blank space is replaced with a hyphen (-)
                search_name = identifier.replace('-', ' ')
                element = RecreativeElement.objects.filter(name__iexact=search_name).first()
            if not element:
                return Response(
                    {"error": "Elemento recreativo no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = RecreativeElementSerializer(
                element,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )