from .models import CustomUser, Rol

from .serializer import UsuarioSerializer

from django.shortcuts import render
from django.conf import settings

import os
from PIL import Image
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# en teoria este es todo el crud que vamos a usar por lo menos para este modelo
class UsuarioView(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = CustomUser.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Función para actualizar la imagen
    @action(detail=True, methods=['put'], url_path='act-img')
    def Actualizar_imagen(self, request, pk=None):
        user = self.get_object()

        # Validar si la imagen está en el request
        imagen = request.FILES.get('imagen')
        if not imagen:
            return Response({'error': 'No se envió ninguna imagen'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que sea una imagen válida
        if not imagen.content_type.startswith('image/'):
            return Response({'error': 'El archivo no es una imagen válida'}, status=status.HTTP_400_BAD_REQUEST)

        # Definir la ruta donde se guardará la imagen
        carpeta_usuario = os.path.join(settings.MEDIA_ROOT, f'usuarios/{user.id}')
        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)  # Crear carpeta si no existe

        # Eliminar la imagen anterior si existe
        if user.ruta_imagen:  # Si hay una ruta de imagen registrada
            ruta_anterior = os.path.join(settings.MEDIA_ROOT, user.ruta_imagen)
            if os.path.exists(ruta_anterior):
                os.remove(ruta_anterior)  # Eliminar la imagen anterior

        # Generar un nombre único basado en la fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Formato: AñoMesDía_HoraMinutoSegundo
        nombre_imagen = f'{timestamp}.webp'
        ruta_imagen = os.path.join(carpeta_usuario, nombre_imagen)

        # Convertir la imagen a .webp y guardarla
        try:
            with Image.open(imagen) as img:
                img = img.convert('RGB')  # Asegurarse de que sea RGB para webp
                img.save(ruta_imagen, 'webp')
        except Exception as e:
            return Response({'error': f'Error al procesar la imagen: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la ruta de la imagen en el modelo del usuario
        user.ruta_imagen = f'usuarios/{user.id}/{nombre_imagen}'
        user.save()
        user_json = UsuarioSerializer(user).data
        return Response({
            'message': 'Imagen actualizada correctamente',
            'usuario': {
                'id': user_json['id'],
                'email': user_json['email'],
                'nombre': user_json['nombre'],
                'apellido': user_json['apellido'],
                'rol': user_json['rol'],
                'imagen': user_json['ruta_imagen']
            }
        }, status=status.HTTP_200_OK)
    

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
        }, status=status.HTTP_201_CREATED)   # enviamos el status
        
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
                'rol': user_json['rol'],
                'imagen': user_json['ruta_imagen']
            }
            }, status=status.HTTP_200_OK   # enviamos el status
        )





    