from django.db import models
from django.utils import timezone

class Prediccion(models.Model):
    edad = models.CharField(max_length=255, null=True, blank=True)
    sexo_biologico = models.CharField(max_length=255, null=True, blank=True)
    escolaridad = models.TextField(null=True, blank=True)
    estrato_socioeconomico = models.TextField(null=True, blank=True)
    prediccion = models.CharField(max_length=50)  # Ejemplo: "Suicidio" o "No Suicidio"
    probabilidad_clase_1 = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    es_entrenamiento = models.BooleanField(default=False)
    
    # Modelo para predicciones individuales por usuario
class PrediccionUsuario(models.Model):
    edad = models.IntegerField()
    sexo_biologico = models.CharField(max_length=10)
    escolaridad = models.CharField(max_length=50)
    estrato_socioeconomico = models.IntegerField()
    estado_civil = models.CharField(max_length=20)
    area_urbana_rural = models.CharField(max_length=10)
    comorbilidades = models.TextField()  # Puedes almacenar las comorbilidades como una cadena separada por comas
    prediccion = models.IntegerField()  # 0 o 1
    probabilidad_clase_1 = models.FloatField()  # Probabilidad de la clase 1
    fecha = models.DateTimeField(default=timezone.now)  # Fecha de la predicción
    es_entrenamiento = models.BooleanField(default=False)

    def __str__(self):
        return f"Predicción Usuario {self.id} - {self.fecha}"
    
    
