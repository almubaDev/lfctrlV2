from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "periodicity", "next_due_date", "is_active")
    list_filter = ("periodicity", "is_active")
    search_fields = ("name", "user__email")
