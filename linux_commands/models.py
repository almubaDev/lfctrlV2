from django.conf import settings
from django.db import models


class CommandTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().lower()
        super().save(*args, **kwargs)


class LinuxCommand(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linux_commands',
    )
    description = models.TextField()
    command = models.TextField()
    tags = models.ManyToManyField(CommandTag, related_name='commands', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description[:50]}" if self.description else self.command


class CommandFlag(models.Model):
    linux_command = models.ForeignKey(
        LinuxCommand,
        on_delete=models.CASCADE,
        related_name='flags',
    )
    flag = models.CharField(max_length=50)
    explanation = models.TextField()

    class Meta:
        ordering = ['flag']

    def __str__(self):
        return f"{self.flag} - {self.linux_command}"
