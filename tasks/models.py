from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Periodicity(models.TextChoices):
        DAILY = "daily", "Diaria"
        WEEKLY = "weekly", "Semanal"
        MONTHLY = "monthly", "Mensual"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    periodicity = models.CharField(max_length=20, choices=Periodicity.choices)
    next_due_date = models.DateField()
    last_completed = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_periodicity_display()})"

    def advance_next_due(self):
        today = timezone.localdate()

        if self.periodicity == self.Periodicity.DAILY:
            delta = timedelta(days=1)
        elif self.periodicity == self.Periodicity.WEEKLY:
            delta = timedelta(weeks=1)
        elif self.periodicity == self.Periodicity.MONTHLY:
            delta = timedelta(days=30)
        else:
            raise ValueError("Invalid periodicity for task")

        self.last_completed = today
        self.next_due_date = today + delta
        self.save(update_fields=["last_completed", "next_due_date"])
