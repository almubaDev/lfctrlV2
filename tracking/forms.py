from django import forms
from .models import WeightRecord, BodyMeasurement, ProgressPhoto

class WeightRecordForm(forms.ModelForm):
    class Meta:
        model = WeightRecord
        fields = ['weight', 'notes']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Ingresa tu peso en kg',
                'step': '0.1',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observaciones, comentarios o notas adicionales (opcional)'
            }),
        }
        labels = {
            'weight': 'Peso (kg)',
            'notes': 'Notas'
        }

class BodyMeasurementForm(forms.ModelForm):
    class Meta:
        model = BodyMeasurement
        fields = ['chest', 'waist', 'hips', 'arms', 'thighs', 'notes']
        widgets = {
            'chest': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Medida en cm',
                'step': '0.1',
                'min': '0'
            }),
            'waist': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Medida en cm',
                'step': '0.1',
                'min': '0'
            }),
            'hips': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Medida en cm',
                'step': '0.1',
                'min': '0'
            }),
            'arms': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Medida en cm',
                'step': '0.1',
                'min': '0'
            }),
            'thighs': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Medida en cm',
                'step': '0.1',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observaciones o notas adicionales (opcional)'
            }),
        }
        labels = {
            'chest': 'Pecho (cm)',
            'waist': 'Cintura (cm)',
            'hips': 'Cadera (cm)',
            'arms': 'Brazos (cm)',
            'thighs': 'Muslos (cm)',
            'notes': 'Notas'
        }

class ProgressPhotoForm(forms.ModelForm):
    class Meta:
        model = ProgressPhoto
        fields = ['photo', 'photo_type', 'notes']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-light file:text-primary-dark hover:file:bg-primary',
                'accept': 'image/*'
            }),
            'photo_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Observaciones o comentarios sobre la foto (opcional)'
            })
        }
        labels = {
            'photo': 'Seleccionar Foto',
            'photo_type': 'Tipo de Foto',
            'notes': 'Notas'
        }
        help_texts = {
            'photo_type': 'Selecciona el ángulo de la foto',
            'photo': 'Selecciona una imagen clara y bien iluminada'
        }