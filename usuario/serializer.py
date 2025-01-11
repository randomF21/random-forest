from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Rol

User = get_user_model()

# clase para el modelo de Rol
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Rol
        fields  = ['id', 'nombre']


# clase para el modelo de usuario de USER (tabla = auth_user)
class UsuarioSerializer(serializers.ModelSerializer):
    # eso sirve para que la contraseña no se vea en las respuestas
    password = serializers.CharField(write_only=True)
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())

    class Meta:
        model   = User
        fields  = ['id', 'password', 'email', 'nombre', 'rol', 'ruta_imagen']
        
    def create(self, validated_data):
        rol_id = validated_data.pop('rol').id
        rol = Rol.objects.get(id=rol_id)
        return User.objects.create_user(
            email           = validated_data['email'],
            password        = validated_data['password'],
            nombre          = validated_data['nombre'],
            rol             = rol
        )
        
