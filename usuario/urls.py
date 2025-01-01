from django.urls import path, include

from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import Login, Registro

from usuario import views

router = routers.DefaultRouter()
router.register(r'', views.UsuarioView, 'usuario')

urlpatterns = [
    path('usuario/', include(router.urls)),
    path('login/', Login, name='login'),
    path('registro/', Registro, name='registro')
]
