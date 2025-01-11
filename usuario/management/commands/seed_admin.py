from django.core.management.base import BaseCommand
from usuario.models import CustomUser, Rol

class Command(BaseCommand):
    help = 'Seed para crear los usuarios de superadmin y admin'

    def handle(self, *args, **kwargs):
        
        roles = {
            'super': Rol.objects.get(id=1),
            'admin': Rol.objects.get(id=2)
        }
        
        usuarios = [
            {
                'password': '1234',
                'email': 'super@gmail.com',
                'nombre':'super',
                'rol': roles['super']
            },
            {
                'password': '1234',
                'email': 'admin@gmail.com',
                'nombre':'admin',
                'rol': roles['admin']
            }
        ]

        for usuario in usuarios: 
            user = CustomUser( 
                email=usuario['email'], 
                nombre=usuario['nombre'], 
                rol=usuario['rol']
            ) 
            user.set_password(usuario['password']) 
            user.save()
        
        self.stdout.write(self.style.SUCCESS('Se inserto el superadmin, el admin y un usuario :D'))
