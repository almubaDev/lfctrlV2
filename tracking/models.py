from django.db import models
from django.conf import settings
import os
import uuid

class WeightRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    weight = models.FloatField(verbose_name="Peso", help_text="Peso en kilogramos")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "Registro de Peso"
        verbose_name_plural = "Registros de Peso"
        unique_together = ['user', 'date']  # Un solo registro por día por usuario

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.weight}kg"

class BodyMeasurement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    chest = models.FloatField(null=True, blank=True, verbose_name="Pecho", help_text="Medida en centímetros")
    waist = models.FloatField(null=True, blank=True, verbose_name="Cintura", help_text="Medida en centímetros")
    hips = models.FloatField(null=True, blank=True, verbose_name="Cadera", help_text="Medida en centímetros")
    arms = models.FloatField(null=True, blank=True, verbose_name="Brazos", help_text="Medida en centímetros")
    thighs = models.FloatField(null=True, blank=True, verbose_name="Muslos", help_text="Medida en centímetros")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "Medida Corporal"
        verbose_name_plural = "Medidas Corporales"
        unique_together = ['user', 'date']  # Un solo registro por día por usuario

    def __str__(self):
        return f"{self.user.email} - {self.date}"

def progress_photo_path(instance, filename):
    """Genera un path único para cada foto"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'progress_photos/{instance.user.id}/{instance.photo_type}/{filename}'

class ProgressPhoto(models.Model):
    PHOTO_TYPE_CHOICES = [
        ('front', 'Frente'),
        ('side', 'Lateral'),
        ('back', 'Espalda')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    photo = models.ImageField(upload_to=progress_photo_path, verbose_name="Foto")
    photo_type = models.CharField(
        max_length=20,
        choices=PHOTO_TYPE_CHOICES,
        verbose_name="Tipo de Foto"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "Foto de Progreso"
        verbose_name_plural = "Fotos de Progreso"

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.get_photo_type_display()}"

    def delete(self, *args, **kwargs):
        """Eliminar el archivo físico cuando se elimina el registro"""
        if self.photo:
            if os.path.isfile(self.photo.path):
                os.remove(self.photo.path)
        super().delete(*args, **kwargs)