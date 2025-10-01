from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import CommandTag, LinuxCommand


class LinuxCommandTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='tester@example.com',
            password='securepass123',
        )
        self.client = Client()
        self.client.force_login(self.user)

    def _formset_management_data(self, total):
        return {
            'flags-TOTAL_FORMS': str(total),
            'flags-INITIAL_FORMS': '0',
            'flags-MIN_NUM_FORMS': '0',
            'flags-MAX_NUM_FORMS': '1000',
        }

    def test_create_command_with_multiple_flags_and_tags(self):
        url = reverse('linux_commands:create')
        data = {
            'description': 'Listar archivos con detalles',
            'command': 'ls -la /var/log',
            'tags': 'sistema, logs, sistema',
            **self._formset_management_data(2),
            'flags-0-id': '',
            'flags-0-flag': '-l',
            'flags-0-explanation': 'Muestra información detallada',
            'flags-1-id': '',
            'flags-1-flag': '-a',
            'flags-1-explanation': 'Incluye archivos ocultos',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        command = LinuxCommand.objects.get()
        self.assertEqual(command.owner, self.user)
        self.assertEqual(command.flags.count(), 2)
        self.assertCountEqual(
            command.flags.values_list('flag', flat=True),
            ['-l', '-a'],
        )
        self.assertCountEqual(
            command.tags.values_list('name', flat=True),
            ['sistema', 'logs'],
        )

    def test_existing_tags_are_reused(self):
        CommandTag.objects.create(name='seguridad')

        url = reverse('linux_commands:create')
        data = {
            'description': 'Ver intentos de inicio de sesión',
            'command': 'journalctl -u ssh',
            'tags': 'Seguridad, monitoreo',
            **self._formset_management_data(1),
            'flags-0-id': '',
            'flags-0-flag': '-r',
            'flags-0-explanation': 'Orden inverso cronológico',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        command = LinuxCommand.objects.get(description='Ver intentos de inicio de sesión')
        self.assertEqual(command.tags.count(), 2)
        self.assertTrue(CommandTag.objects.filter(name='seguridad').exists())
        self.assertEqual(CommandTag.objects.filter(name='seguridad').count(), 1)

    def test_command_list_filters_by_tag(self):
        seguridad = CommandTag.objects.create(name='seguridad')
        sistema = CommandTag.objects.create(name='sistema')

        command_security = LinuxCommand.objects.create(
            owner=self.user,
            description='Revisar accesos ssh',
            command='last -a | head',
        )
        command_security.tags.add(seguridad)

        command_system = LinuxCommand.objects.create(
            owner=self.user,
            description='Uso de disco',
            command='df -h',
        )
        command_system.tags.add(sistema)

        url = reverse('linux_commands:list')
        response = self.client.get(url, {'tags': 'seguridad'})
        self.assertEqual(response.status_code, 200)

        commands = list(response.context['commands'])
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], command_security)

        response_multiple = self.client.get(url, {'tags': 'seguridad, sistema'})
        self.assertEqual(response_multiple.status_code, 200)
        commands_multiple = list(response_multiple.context['commands'])
        self.assertCountEqual(commands_multiple, [command_security, command_system])
