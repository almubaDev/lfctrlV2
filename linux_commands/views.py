from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
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

    commands = (
        LinuxCommand.objects.select_related('owner')
        .prefetch_related('flags', 'tags')
    )

    if selected_tags:
        commands = commands.filter(tags__name__in=selected_tags).distinct()

    all_tags = CommandTag.objects.annotate(command_count=Count('commands'))

    context = {
        'commands': commands,
        'all_tags': all_tags,
        'selected_tags': selected_tags,
        'tag_query': ', '.join(selected_tags),
    }
    return render(request, 'linux_commands/command_list.html', context)


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

                tags = []
                for tag_name in tag_names:
                    tag, _ = CommandTag.objects.get_or_create(name=tag_name)
                    tags.append(tag)

                if tags:
                    command.tags.set(tags)
                else:
                    command.tags.clear()

            messages.success(request, 'Comando creado correctamente.')
            return redirect(reverse('linux_commands:list'))
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    context = {
        'form': form,
        'formset': formset,
        'all_tags': CommandTag.objects.order_by('name'),
        'initial_tags': request.POST.get('tags', '') if request.method == 'POST' else '',
    }
    return render(request, 'linux_commands/command_form.html', context)


@login_required
def tag_suggestions(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tags = list(CommandTag.objects.values_list('name', flat=True))
        return JsonResponse({'tags': tags})
    return JsonResponse({'tags': []})
