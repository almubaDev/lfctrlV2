from django.contrib import admin
from .models import WeightRecord, BodyMeasurement, ProgressPhoto

@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight', 'notes']
    list_filter = ['date', 'user']
    search_fields = ['user__email', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'

@admin.register(BodyMeasurement)
class BodyMeasurementAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'chest', 'waist', 'hips', 'arms', 'thighs']
    list_filter = ['date', 'user']
    search_fields = ['user__email', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'

@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'photo_type', 'photo']
    list_filter = ['date', 'photo_type', 'user']
    search_fields = ['user__email', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'