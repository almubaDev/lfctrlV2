from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import ExtractWeek, ExtractMonth
from django.http import JsonResponse
from datetime import datetime, timedelta
from calendar import monthrange
import json

from .models import WeightRecord, BodyMeasurement, ProgressPhoto
from .forms import WeightRecordForm, BodyMeasurementForm, ProgressPhotoForm

# ==================== WEIGHT TRACKING ====================

@login_required
def weight_tracker(request):
    if request.method == 'POST':
        form = WeightRecordForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe un registro para hoy
            today = datetime.now().date()
            existing = WeightRecord.objects.filter(user=request.user, date=today).first()
            
            if existing:
                # Actualizar el registro existente
                existing.weight = form.cleaned_data['weight']
                existing.notes = form.cleaned_data['notes']
                existing.save()
                messages.success(request, '¡Peso actualizado exitosamente!')
            else:
                # Crear nuevo registro
                weight_record = form.save(commit=False)
                weight_record.user = request.user
                weight_record.save()
                messages.success(request, '¡Peso registrado exitosamente!')
            
            return redirect('tracking:weight_tracker')
    else:
        form = WeightRecordForm()

    # Obtener todos los registros
    all_records = WeightRecord.objects.filter(user=request.user).order_by('-date', '-id')
    records_list = list(all_records)
    
    # Calcular estadísticas
    stats = {}
    if records_list:
        first_record = records_list[-1]  # El más antiguo
        last_record = records_list[0]    # El más reciente
        
        stats['inicio'] = {
            'peso': first_record.weight,
            'fecha': first_record.date
        }
        stats['actual'] = {
            'peso': last_record.weight,
            'fecha': last_record.date
        }
        stats['cambio_total'] = last_record.weight - first_record.weight
        stats['max'] = all_records.aggregate(Max('weight'))['weight__max']
        stats['min'] = all_records.aggregate(Min('weight'))['weight__min']
        
        # Estadísticas del último mes
        un_mes_atras = datetime.now().date() - timedelta(days=30)
        registros_mes = all_records.filter(date__gte=un_mes_atras)
        if registros_mes.exists():
            primer_registro_mes = registros_mes.last()
            stats['cambio_mes'] = last_record.weight - primer_registro_mes.weight
            stats['promedio_mes'] = registros_mes.aggregate(Avg('weight'))['weight__avg']
        else:
            stats['cambio_mes'] = 0
            stats['promedio_mes'] = last_record.weight

    # Preparar datos para gráficas
    chart_data = {
        'daily': [],
        'weekly': {},
        'monthly': {}
    }

    # Datos diarios
    for record in reversed(records_list):  # Orden cronológico para la gráfica
        chart_data['daily'].append({
            'date': record.date.strftime('%Y-%m-%d'),
            'weight': float(record.weight)
        })

    # Datos semanales
    weekly_data = all_records.annotate(
        week=ExtractWeek('date')
    ).values('week').annotate(
        avg_weight=Avg('weight')
    ).order_by('week')

    for entry in weekly_data:
        chart_data['weekly'][f"Semana {entry['week']}"] = float(entry['avg_weight'])

    # Datos mensuales
    monthly_data = all_records.annotate(
        month=ExtractMonth('date')
    ).values('month').annotate(
        avg_weight=Avg('weight')
    ).order_by('month')

    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    for entry in monthly_data:
        chart_data['monthly'][months[entry['month']-1]] = float(entry['avg_weight'])

    # Preparar registros con cambios
    weight_records = []
    for i, record in enumerate(records_list):
        entry = {
            'date': record.date,
            'weight': record.weight,
            'notes': record.notes,
            'id': record.id,
            'change': None,
            'change_symbol': None
        }
        
        if i < len(records_list) - 1:
            previous_weight = records_list[i + 1].weight
            change = record.weight - previous_weight
            entry['change'] = abs(change)
            entry['change_symbol'] = '↑' if change > 0 else '↓' if change < 0 else '='
        else:
            entry['change'] = 0
            
        weight_records.append(entry)

    context = {
        'form': form,
        'weight_records': weight_records,
        'stats': stats,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'tracking/weight_tracker.html', context)

@login_required
def weight_delete(request, pk):
    record = get_object_or_404(WeightRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        record.delete()
        messages.success(request, '¡Registro eliminado exitosamente!')
    return redirect('tracking:weight_tracker')

# ==================== BODY MEASUREMENTS ====================

@login_required
def measurements(request):
    if request.method == 'POST':
        form = BodyMeasurementForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe un registro para hoy
            today = datetime.now().date()
            existing = BodyMeasurement.objects.filter(user=request.user, date=today).first()
            
            if existing:
                # Actualizar el registro existente
                for field in ['chest', 'waist', 'hips', 'arms', 'thighs', 'notes']:
                    setattr(existing, field, form.cleaned_data[field])
                existing.save()
                messages.success(request, '¡Medidas actualizadas exitosamente!')
            else:
                # Crear nuevo registro
                measurement = form.save(commit=False)
                measurement.user = request.user
                measurement.save()
                messages.success(request, '¡Medidas registradas exitosamente!')
            
            return redirect('tracking:measurements')
    else:
        form = BodyMeasurementForm()

    # Obtener medidas ordenadas
    all_measurements = BodyMeasurement.objects.filter(user=request.user).order_by('-date', '-id')
    measurements_list = list(all_measurements)
    
    # Preparar datos para gráficas
    chart_data = {
        'dates': [],
        'chest': [],
        'waist': [],
        'hips': [],
        'arms': [],
        'thighs': []
    }

    # Datos en orden cronológico para gráficas
    for record in reversed(measurements_list):
        chart_data['dates'].append(record.date.strftime('%Y-%m-%d'))
        chart_data['chest'].append(float(record.chest) if record.chest else None)
        chart_data['waist'].append(float(record.waist) if record.waist else None)
        chart_data['hips'].append(float(record.hips) if record.hips else None)
        chart_data['arms'].append(float(record.arms) if record.arms else None)
        chart_data['thighs'].append(float(record.thighs) if record.thighs else None)
    
    # Preparar datos para tabla con cambios
    measurements_with_changes = []
    for i, record in enumerate(measurements_list):
        entry = {
            'date': record.date,
            'chest': {'value': record.chest, 'change': None, 'change_symbol': None},
            'waist': {'value': record.waist, 'change': None, 'change_symbol': None},
            'hips': {'value': record.hips, 'change': None, 'change_symbol': None},
            'arms': {'value': record.arms, 'change': None, 'change_symbol': None},
            'thighs': {'value': record.thighs, 'change': None, 'change_symbol': None},
            'notes': record.notes,
            'id': record.id
        }
        
        # Calcular cambios si hay registro anterior
        if i < len(measurements_list) - 1:
            prev_record = measurements_list[i + 1]
            
            for field in ['chest', 'waist', 'hips', 'arms', 'thighs']:
                current_value = getattr(record, field)
                prev_value = getattr(prev_record, field)
                if current_value is not None and prev_value is not None:
                    change = current_value - prev_value
                    entry[field]['change'] = abs(change)
                    entry[field]['change_symbol'] = '↑' if change > 0 else '↓' if change < 0 else '='
        
        measurements_with_changes.append(entry)

    context = {
        'form': form,
        'measurements': measurements_with_changes,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'tracking/measurements.html', context)

@login_required
def measurement_delete(request, pk):
    measurement = get_object_or_404(BodyMeasurement, pk=pk, user=request.user)
    if request.method == 'POST':
        measurement.delete()
        messages.success(request, '¡Registro eliminado exitosamente!')
    return redirect('tracking:measurements')

# ==================== PROGRESS PHOTOS ====================

@login_required
def photos(request):
    if request.method == 'POST':
        form = ProgressPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            messages.success(request, '¡Foto guardada exitosamente!')
            return redirect('tracking:photos')
    else:
        form = ProgressPhotoForm()

    # Obtener mes y año de la URL o usar actual
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # Obtener fechas con fotos para el mes
    photo_dates = ProgressPhoto.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).values('date').annotate(count=Count('id')).order_by('date')

    # Crear calendario
    cal_data = []
    _, num_days = monthrange(year, month)
    first_day = datetime(year, month, 1)
    start_weekday = first_day.weekday()

    # Crear semanas
    current_week = []
    
    # Días vacíos al inicio
    for i in range(start_weekday):
        current_week.append({'day': '', 'has_photos': False})

    # Días del mes
    photo_dates_dict = {d['date']: d['count'] for d in photo_dates}
    
    for day in range(1, num_days + 1):
        current_date = datetime(year, month, day).date()
        current_week.append({
            'day': day,
            'date': current_date,
            'has_photos': current_date in photo_dates_dict,
            'photo_count': photo_dates_dict.get(current_date, 0)
        })
        
        if len(current_week) == 7:
            cal_data.append(current_week)
            current_week = []

    # Última semana
    if current_week:
        while len(current_week) < 7:
            current_week.append({'day': '', 'has_photos': False})
        cal_data.append(current_week)

    # Navegación
    prev_month = datetime(year, month, 1) - timedelta(days=1)
    next_month = (datetime(year, month, 1) + timedelta(days=32)).replace(day=1)

    context = {
        'form': form,
        'calendar': cal_data,
        'current_month': first_day,
        'prev_month': prev_month,
        'next_month': next_month
    }

    return render(request, 'tracking/photos.html', context)

@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(ProgressPhoto, pk=pk, user=request.user)
    if request.method == 'POST':
        photo.delete()  # El método delete del modelo se encarga de eliminar el archivo
        messages.success(request, '¡Foto eliminada exitosamente!')
        return JsonResponse({'status': 'success'})
    return redirect('tracking:photos')

@login_required
def get_photos_for_date(request):
    """API endpoint para obtener fotos de una fecha específica"""
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
        
    photos = ProgressPhoto.objects.filter(
        user=request.user,
        date=date_obj
    ).order_by('photo_type')
    
    photos_data = [{
        'id': photo.id,
        'url': photo.photo.url,
        'type': photo.get_photo_type_display(),
        'notes': photo.notes,
        'date': photo.date.strftime('%Y-%m-%d')
    } for photo in photos]
    
    return JsonResponse({'photos': photos_data})

@login_required
def photo_compare(request):
    """Vista para comparar fotos de diferentes fechas"""
    photo_type = request.GET.get('type', 'front')
    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')

    # Obtener todas las fotos del tipo seleccionado
    photos = ProgressPhoto.objects.filter(
        user=request.user,
        photo_type=photo_type
    ).order_by('-date')

    # Si se seleccionaron fechas específicas
    photo1 = None
    photo2 = None
    if date1:
        try:
            date1_obj = datetime.strptime(date1, '%Y-%m-%d').date()
            photo1 = photos.filter(date=date1_obj).first()
        except ValueError:
            pass
            
    if date2:
        try:
            date2_obj = datetime.strptime(date2, '%Y-%m-%d').date()
            photo2 = photos.filter(date=date2_obj).first()
        except ValueError:
            pass

    context = {
        'photo_type': photo_type,
        'photos': photos,
        'photo1': photo1,
        'photo2': photo2,
        'available_dates': list(photos.values_list('date', flat=True).distinct())
    }
    return render(request, 'tracking/photo_compare.html', context)