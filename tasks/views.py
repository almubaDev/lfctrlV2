from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


@login_required
def task_list(request):
    today = timezone.localdate()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.next_due_date = today
            task.save()
            form = TaskForm()
    else:
        form = TaskForm()

    tasks = (
        Task.objects.filter(user=request.user, is_active=True, next_due_date__lte=today)
        .order_by("next_due_date", "name")
    )

    return render(
        request,
        "tasks/task_list.html",
        {
            "today": today,
            "tasks": tasks,
            "form": form,
        },
    )


@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_active=True)
    task.advance_next_due()
    return redirect("tasks:today")
