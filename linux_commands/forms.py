from django import forms
from django.forms import inlineformset_factory

from .models import CommandFlag, LinuxCommand


class LinuxCommandForm(forms.ModelForm):
    class Meta:
        model = LinuxCommand
        fields = ['description', 'command']
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary',
                }
            ),
            'command': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary font-mono',
                }
            ),
        }


class CommandFlagForm(forms.ModelForm):
    class Meta:
        model = CommandFlag
        fields = ['flag', 'explanation']
        widgets = {
            'flag': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary font-mono',
                }
            ),
            'explanation': forms.Textarea(
                attrs={
                    'rows': 2,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary',
                }
            ),
        }


CommandFlagFormSet = inlineformset_factory(
    LinuxCommand,
    CommandFlag,
    form=CommandFlagForm,
    fields=['flag', 'explanation'],
    extra=0,
    can_delete=True,
)
