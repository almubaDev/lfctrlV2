from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommandFlagFormSet, LinuxCommandForm
from .models import CommandTag, LinuxCommand


def _normalize_tag_list(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []
    normalized = {
        tag.strip().lower()
        for tag in raw_tags.split(',')
        if tag.strip()
    }
    return sorted(normalized)


@login_required
def command_list(request):
    tag_query = request.GET.get('tags', '')
    selected_tags = _normalize_tag_list(tag_query)
    search_query = request.GET.get('q', '').strip()

    commands = (
        LinuxCommand.objects.select_related('owner')
        .prefetch_related('flags', 'tags')
        .order_by('description', 'id')
    )

    if selected_tags:
        commands = commands.filter(tags__name__in=selected_tags).distinct()

    if search_query:
        commands = commands.filter(description__icontains=search_query)

    all_tags = CommandTag.objects.annotate(command_count=Count('commands'))

    context = {
        'commands': commands,
        'all_tags': all_tags,
        'selected_tags': selected_tags,
        'tag_query': ', '.join(selected_tags),
        'search_query': search_query,
    }
    return render(request, 'linux_commands/command_list.html', context)


def _apply_tags(command: LinuxCommand, tag_names: list[str]) -> None:
    tags = []
    for tag_name in tag_names:
        tag, _ = CommandTag.objects.get_or_create(name=tag_name)
        tags.append(tag)

    if tags:
        command.tags.set(tags)
    else:
        command.tags.clear()


def _user_can_manage(user, command: LinuxCommand) -> bool:
    return command.owner == user or getattr(user, 'is_superuser', False)


@login_required
def command_create(request):
    form = LinuxCommandForm(request.POST or None)
    formset = CommandFlagFormSet(request.POST or None, prefix='flags')

    if request.method == 'POST':
        tag_names = _normalize_tag_list(request.POST.get('tags', ''))

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                command = form.save(commit=False)
                command.owner = request.user
                command.save()
                formset.instance = command
                formset.save()
                _apply_tags(command, tag_names)

            messages.success(request, 'Comando creado correctamente.')
            return redirect(reverse('linux_commands:list'))
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    context = {
        'form': form,
        'formset': formset,
        'all_tags': CommandTag.objects.order_by('name'),
        'initial_tags': request.POST.get('tags', '') if request.method == 'POST' else '',
        'is_edit': False,
    }
    return render(request, 'linux_commands/command_form.html', context)


@login_required
def command_update(request, pk):
    command = get_object_or_404(LinuxCommand, pk=pk)

    if not _user_can_manage(request.user, command):
        messages.error(request, 'No tienes permisos para editar este comando.')
        return redirect(reverse('linux_commands:list'))

    form = LinuxCommandForm(request.POST or None, instance=command)
    formset = CommandFlagFormSet(request.POST or None, prefix='flags', instance=command)

    if request.method == 'POST':
        tag_names = _normalize_tag_list(request.POST.get('tags', ''))

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                _apply_tags(command, tag_names)

            messages.success(request, 'Comando actualizado correctamente.')
            return redirect(reverse('linux_commands:list'))
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    initial_tags = (
        request.POST.get('tags', '')
        if request.method == 'POST'
        else ', '.join(command.tags.order_by('name').values_list('name', flat=True))
    )

    context = {
        'form': form,
        'formset': formset,
        'all_tags': CommandTag.objects.order_by('name'),
        'initial_tags': initial_tags,
        'is_edit': True,
    }
    return render(request, 'linux_commands/command_form.html', context)


@login_required
def command_delete(request, pk):
    command = get_object_or_404(LinuxCommand, pk=pk)

    if not _user_can_manage(request.user, command):
        messages.error(request, 'No tienes permisos para eliminar este comando.')
        return redirect(reverse('linux_commands:list'))

    if request.method == 'POST':
        command.delete()
        messages.success(request, 'Comando eliminado correctamente.')
    else:
        messages.error(request, 'Acción no permitida.')

    return redirect(reverse('linux_commands:list'))


@login_required
def tag_suggestions(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tags = list(CommandTag.objects.values_list('name', flat=True))
        return JsonResponse({'tags': tags})
    return JsonResponse({'tags': []})
