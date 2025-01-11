from django.db import models

class Prediccion(models.Model):
    edad = models.CharField(max_length=255, null=True, blank=True)
    sexo_biologico = models.CharField(max_length=255, null=True, blank=True)
    escolaridad = models.TextField(null=True, blank=True)
    estrato_socioeconomico = models.TextField(null=True, blank=True)
    prediccion = models.CharField(max_length=50)  # Ejemplo: "Suicidio" o "No Suicidio"
    probabilidad_clase_1 = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    es_entrenamiento = models.BooleanField(default=False)
    
    
