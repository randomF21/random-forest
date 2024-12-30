from django.shortcuts import render
#from django.contrib.auth.models import User

from .models import CustomUser, Rol

from .serializer import UsuarioSerializer
#from .models import Usuario

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

# en teoria este es todo el crud que vamos a usar por lo menos para este modelo
class UsuarioView(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = CustomUser.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    

# Funciones para el registro de usuarios
@api_view(['POST'])
def Registro(request):
    # tomamos el valor de email y guardamos
    email = request.data.get('email')
    # validamos si este existe
    if CustomUser.objects.filter(email=email).exists():
        # en caso de que exista enviamos el siguiente mensaje y error
        return Response({
            'error': 'El correo ya esta registrado',
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
    # Asignamos un rol "quemado" para el registro
    rol_id = 3
    # Agregamos el rol manualmente a los datos que enviamos al serializer
    data = request.data.copy()  # Hacemos una copia de los datos enviados
    data['rol'] = rol_id        # Agregamos el rol quemado
    
    # guardar en una variable los datos 
    serializer = UsuarioSerializer(data=data)
    # validamos si los datos son valido
    if serializer.is_valid():
        user = serializer.save()                # si lo son, los enviamos a la funcion para crear
        refresh = RefreshToken.for_user(user)   # generamos el token 
        # convertimos el registro en un JSON para manejarlo
        user_json = UsuarioSerializer(user).data
        return Response({
            #'refre': str(refresh), # permite "recargar" el token
            'token': str(refresh.access_token), # token de acceso con caducidad 
            'usuario': {
                'id': user_json['id'],
                'email': user_json['email'],
                'nombre': user_json['nombre'],
                'apellido': user_json['apellido'],
                'rol': user_json['rol']
            }
            }, status=status.HTTP_201_CREATED   # enviamos el status
        )
        
    # si fallo enviamos status correspondiente
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# Funciones para el login de la aplicacion
@api_view(['POST'])
def Login(request):
    # tomamos los valores que nos mandan
    email = request.data.get("email")
    password = request.data.get("password")
    # validamos que venga correctos
    if not email or not password:
        # retornamos un error en caso de que no sean validos
        return Response({
            "error": "El email y la contraseña son requeridos"
            }, status=status.HTTP_401_UNAUTHORIZED
        )
    # hacemos un try para buscar
    try:
        # buscamos al usuario
        user = CustomUser.objects.get(email=email)
        # verificamos el contraseña
        if not user.check_password(password):
            # si esta incorrecta hara:
            return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST)
    # en la excepcion manejamos si el usuario no existe
    except CustomUser.DoesNotExist:
        # si no existe el usuario hara:
        return Response({"error": "Credenciales Incorrectas"}, status=status.HTTP_404_NOT_FOUND)
    # convertimos el registro en un JSON para manejarlo
    user_json = UsuarioSerializer(user).data
    # generamos el token
    refresh = RefreshToken.for_user(user)
    return Response({
            'token': str(refresh.access_token), # token de acceso con caducidad 
            'usuario': {
                'id': user_json['id'],
                'email': user_json['email'],
                'nombre': user_json['nombre'],
                'apellido': user_json['apellido'],
                'rol': user_json['rol']
            }
            }, status=status.HTTP_200_OK   # enviamos el status
        )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Perfil(request):
    
    print('----// Estamos en perfil pa colocar el CRUD AQUI //----')
    
    return Response("autorizado para entrar al sistemaaaaa", status=status.HTTP_200_OK)
    
    
    