from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
        )
        self.today = timezone.localdate()

    def test_advance_next_due_daily(self):
        task = Task.objects.create(
            user=self.user,
            name="Tarea diaria",
            periodicity=Task.Periodicity.DAILY,
            next_due_date=self.today,
        )

        with patch("django.utils.timezone.localdate", return_value=self.today):
            task.advance_next_due()

        task.refresh_from_db()
        self.assertEqual(task.last_completed, self.today)
        self.assertEqual(task.next_due_date, self.today + timedelta(days=1))

    def test_advance_next_due_weekly(self):
        task = Task.objects.create(
            user=self.user,
            name="Tarea semanal",
            periodicity=Task.Periodicity.WEEKLY,
            next_due_date=self.today,
        )

        with patch("django.utils.timezone.localdate", return_value=self.today):
            task.advance_next_due()

        task.refresh_from_db()
        self.assertEqual(task.last_completed, self.today)
        self.assertEqual(task.next_due_date, self.today + timedelta(weeks=1))


class TaskViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="tester@example.com",
            password="password123",
        )
        self.client.force_login(self.user)
        self.today = timezone.localdate()

    def test_task_list_returns_only_due_tasks(self):
        due_task = Task.objects.create(
            user=self.user,
            name="Pendiente",
            periodicity=Task.Periodicity.DAILY,
            next_due_date=self.today,
        )
        Task.objects.create(
            user=self.user,
            name="Futura",
            periodicity=Task.Periodicity.DAILY,
            next_due_date=self.today + timedelta(days=1),
        )
        Task.objects.create(
            user=self.user,
            name="Inactiva",
            periodicity=Task.Periodicity.DAILY,
            next_due_date=self.today,
            is_active=False,
        )

        response = self.client.get(reverse("tasks:today"))
        tasks = response.context["tasks"]

        self.assertIn(due_task, tasks)
        self.assertEqual(len(tasks), 1)

    def test_task_list_creates_task_with_today_due_date(self):
        response = self.client.post(
            reverse("tasks:today"),
            {"name": "Nueva", "periodicity": Task.Periodicity.WEEKLY},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(name="Nueva")
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.next_due_date, self.today)
