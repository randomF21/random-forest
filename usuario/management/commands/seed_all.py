from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'SEED para correr las demas Seed'
    
    def handle(self, *args, **options):
        call_command('seed_roles')
        call_command('seed_admin')
        self.stdout.write(self.style.SUCCESS('Todas las semillas han sido ejecutadas'))