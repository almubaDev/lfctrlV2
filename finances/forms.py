from django import forms
from .models import AnnualFlow, Income, ExpenseCategory, Expense, RemnantWithdrawal, Presupuesto, PresupuestoItem

class AnnualFlowForm(forms.ModelForm):
    class Meta:
        model = AnnualFlow
        fields = ['year']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': 2000,
                'max': 2100,
                'placeholder': 'Ingrese el año'
            })
        }

    def clean_year(self):
        year = self.cleaned_data['year']
        if AnnualFlow.objects.filter(year=year).exists():
            raise forms.ValidationError(f'Ya existe un flujo para el año {year}')
        return year

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Descripción del ingreso'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0',
                'step': 'any',
                'placeholder': '0.00'
            })
        }
        labels = {
            'description': 'Descripción',
            'amount': 'Monto'
        }

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Descripción opcional'
            })
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción'
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'description', 'amount']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Descripción del gasto'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0',
                'step': 'any',
                'placeholder': '0.00'
            })
        }
        labels = {
            'category': 'Categoría',
            'description': 'Descripción',
            'amount': 'Monto'
        }

class RemnantWithdrawalForm(forms.ModelForm):
    class Meta:
        model = RemnantWithdrawal
        fields = ['amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0',
                'step': 'any',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Motivo del retiro'
            })
        }
        labels = {
            'amount': 'Monto a retirar',
            'description': 'Descripción'
        }

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Nombre del presupuesto'
            })
        }
        labels = {
            'nombre': 'Nombre del Presupuesto'
        }

class PresupuestoItemForm(forms.ModelForm):
    class Meta:
        model = PresupuestoItem
        fields = ['nombre', 'url', 'descripcion', 'costo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Nombre del item'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'https://ejemplo.com (opcional)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descripción del item'
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0',
                'step': 'any',
                'placeholder': '0.00'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'url': 'URL de referencia',
            'descripcion': 'Descripción',
            'costo': 'Costo'
        }