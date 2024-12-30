from django.core.management.base import BaseCommand
from usuario.models import CustomUser, Rol

class Command(BaseCommand):
    help = 'Seed para crear los usuarios de superadmin y admin'

    def handle(self, *args, **kwargs):
        
        roles = {
            'super': Rol.objects.get(id=1),
            'admin': Rol.objects.get(id=2),
            'user': Rol.objects.get(id=3)
        }
        
        usuarios = [
            {
                'password': '1234',
                'email': 'super@gmail.com',
                'nombre':'super',
                'apellido':'admin',
                'tipo_documento':'Registro Civil',
                'num_documento':'1234567890',
                'telefono':'3214105263',
                'nacimiento':'2001-01-01',
                'rol': roles['super']
            },
            {
                'password': '1234',
                'email': 'admin@gmail.com',
                'nombre':'admin',
                'apellido':'normal',
                'tipo_documento':'Registro Civil',
                'num_documento':'1234567890',
                'telefono':'3214105263',
                'nacimiento':'2001-01-01',
                'rol': roles['admin']
            },
            {
                'password': '1234',
                'email': 'user@gmail.com',
                'nombre':'usuario',
                'apellido':'normal',
                'tipo_documento':'Registro Civil',
                'num_documento':'1234567890',
                'telefono':'3214105263',
                'nacimiento':'2001-01-01',
                'rol': roles['user']
            }
        ]

        for usuario in usuarios: 
            user = CustomUser( 
                email=usuario['email'], 
                nombre=usuario['nombre'], 
                apellido=usuario['apellido'], 
                tipo_documento=usuario['tipo_documento'], 
                num_documento=usuario['num_documento'], 
                telefono=usuario['telefono'], 
                nacimiento=usuario['nacimiento'], 
                rol=usuario['rol']
            ) 
            user.set_password(usuario['password']) 
            user.save()
        
        self.stdout.write(self.style.SUCCESS('Se inserto el superadmin, el admin y un usuario :D'))
