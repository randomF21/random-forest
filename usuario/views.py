from django.shortcuts import render
from django.contrib.auth.models import User

from .serializer import UsuarioSerializer
#from .models import Usuario

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

# en teoria este es todo el crud que vamos a usar por lo menos para este modelo
class UsuarioView(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    

# Funciones para el registro de usuarios
@api_view(['POST'])
def Registro(request):
    # tomamos el valor de email y guaramos
    email = request.data.get('email')
    # validamos si este existe
    if User.objects.filter(email=email).exists():
        # en caso de que exista enviamos el siguiente mensaje y error
        return Response({
            'mensaje': 'El correo ya esta registrado',
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
    # guardar en una variable los datos 
    serializer = UsuarioSerializer(data=request.data)
    # validamos si los datos son valido
    if serializer.is_valid():
        user = serializer.save()                # si lo son, los enviamos a la funcion para crear
        refresh = RefreshToken.for_user(user)   # generamos el token 
        return Response({
            #'refre': str(refresh), # permite "recargar" el token
            'token': str(refresh.access_token), # token de acceso con caducidad 
            'usuario': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            }, status=status.HTTP_201_CREATED   # enviamos el status
        )
        
    # si fallo enviamos status correspondiente
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# Funciones para el login de la aplicacion
@api_view(['POST'])
def Login(request):
    # tomamos los valores que nos mandan
    username = request.data.get("username")
    password = request.data.get("password")
    # validamos que venga correctos
    if not username or not password:
        # retornamos un error en caso de que no sean validos
        return Response({
            "error": "El usuario y la contraseña son requeridos"
            }, status=status.HTTP_401_UNAUTHORIZED
        )
    # hacemos un try para buscar
    try:
        # buscamos al usuario
        user = User.objects.get(username=username)
        # verificamos el contraseña
        if not user.check_password(password):
            # si esta incorrecta hara:
            return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST)
    # en la excepcion manejamos si el usuario no existe
    except User.DoesNotExist:
        # si no existe el usuario hara:
        return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_404_NOT_FOUND)
    # generamos el token 
    refresh = RefreshToken.for_user(user)
    return Response({
            #'refre': str(refresh), # permite "recargar" el token
            'token': str(refresh.access_token), # token de acceso con caducidad 
            'usuario': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            }, status=status.HTTP_200_OK   # enviamos el status
        )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Perfil(request):
    
    print('----// Estamos en perfil pa colocar el CRUD AQUI //----')
    
    return Response("autorizado para entrar al sistemaaaaa", status=status.HTTP_200_OK)
    
    
    