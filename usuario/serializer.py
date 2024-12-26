from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser, Rol

# clase para el modelo de Rol
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Rol
        fields  = ['id', 'nombre']


# clase para el modelo de usuario de USER (tabla = auth_user)
class UsuarioSerializer(serializers.ModelSerializer):
    # eso sirve para que la contraseña no se vea en las respuestas
    password = serializers.CharField(write_only=True)
    rol = RolSerializer(read_only=True) # 

    class Meta:
        model   = CustomUser
        fields  = ['id', 'username', 'email', 'password', 'rol']
        
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
