"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from RecreativeElement.views import RecreativeElementView
from Reservation.views import ReservationViewSet, ReservationElementViewSet  
from Room.views import RoomViewSet, RoomXElementsViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include

from Register.views import RegisterView
from User.views import UserView

router = DefaultRouter()
router.register(r'room', RoomViewSet)
router.register(r'room-elements', RoomXElementsViewSet)
router.register(r'reservation', ReservationViewSet)
router.register(r'reservation-elements', ReservationElementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recreative-elements/', RecreativeElementView.as_view(), name='element'),
    path('recreative-elements/<identifier>/', RecreativeElementView.as_view(), name='element-detail'),
    path('register/', RegisterView.as_view(), name='registers'),
    path('register/<int:identifier>/', RegisterView.as_view(), name='register-detail'),
    path('user/', UserView.as_view(), name='users'),
    path('user/<identifier>/', UserView.as_view(), name='user-detail'),
] + router.urls 

