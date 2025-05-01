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
from Room.views import CreateRoomView
from RecreativeElement.views import RecreativeElementView
from Register.views import RegisterView
from User.views import UserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crear-sala/', CreateRoomView.as_view(), name='rooms'),
    path('recreative-elements/', RecreativeElementView.as_view(), name='element'),
    path('recreative-elements/<identifier>/', RecreativeElementView.as_view(), name='element-detail'),
    path('register/', RegisterView.as_view(), name='registers'),
    path('register/<int:identifier>/', RegisterView.as_view(), name='register-detail'),
    path('user/', UserView.as_view(), name='users'),
    path('user/<identifier>/', UserView.as_view(), name='user-detail'),
]

