from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, rol=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        if not rol:
            raise ValueError('El rol es obligatorio')
        if not password:
            raise ValueError('La contraseña es obligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email           = models.EmailField(null=False, unique=True)
    nombre          = models.CharField(max_length=70, null=False, blank=False)
    ruta_imagen     = models.TextField(null=True, blank=True)
    # Puedes agregar otros campos que necesites
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, null=False, blank=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [email, nombre, rol]

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'