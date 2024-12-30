from django.core.management.base import BaseCommand
from usuario.models import Rol

class Command(BaseCommand):
    help = 'Seed para crear los roles del sistema'

    def handle(self, *args, **kwargs):
        roles = [
            'superadministrador',
            'administrador',
            'usuario'
        ]

        for role in roles:
            Rol.objects.get_or_create(nombre=role)
        
        self.stdout.write(self.style.SUCCESS('Se insertaron los roles :D'))
