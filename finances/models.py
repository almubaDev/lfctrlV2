from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone

class AnnualFlow(models.Model):
    year = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Flujo Anual"
        verbose_name_plural = "Flujos Anuales"
        ordering = ['-year']
    
    def create_monthly_income_books(self):
        for month in range(1, 13):
            MonthlyIncomeBook.objects.create(
                annual_flow=self,
                month=month
            )
    
    def get_accumulated_remnant(self):
        """Suma todos los remanentes del año"""
        return self.income_books.aggregate(
            total=models.Sum('remnants__amount')
        )['total'] or 0
    
    def get_total_income(self):
        return self.income_books.aggregate(
            total=Sum('incomes__amount')
        )['total'] or 0
    
    def get_total_expenses(self):
        return Expense.objects.filter(
            income__book__annual_flow=self
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    def close_year(self):
        if not all(book.is_closed for book in self.income_books.all()):
            raise ValidationError('No se puede cerrar el año hasta que todos los meses estén cerrados')
        self.is_closed = True
        self.save()
    
    def __str__(self):
        return f"Flujo Anual {self.year}"

class MonthlyIncomeBook(models.Model):
    MONTH_CHOICES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'),
        (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'),
        (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'),
        (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    annual_flow = models.ForeignKey(
        AnnualFlow,
        on_delete=models.CASCADE,
        related_name='income_books'
    )
    month = models.IntegerField(choices=MONTH_CHOICES)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Libro de Ingresos Mensual"
        verbose_name_plural = "Libros de Ingresos Mensuales"
        unique_together = ['annual_flow', 'month']
        ordering = ['month']
    
    def get_total_income(self):
        """Obtiene solo los ingresos del mes"""
        return self.incomes.aggregate(
            total=Sum('amount')
        )['total'] or 0
    
    def get_total_expenses(self):
        """Obtiene solo los gastos del mes"""
        return Expense.objects.filter(
            income__book=self
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    def get_current_balance(self):
        """Calcula el balance del mes sin incluir remanentes anteriores"""
        return self.get_total_income() - self.get_total_expenses()
    
    def get_month_remnant(self):
        """Obtiene el remanente del mes actual"""
        if self.is_closed and self.remnants.exists():
            return self.remnants.latest('transfer_date').amount
        return 0
    
    def get_previous_remnant(self):
        """Obtiene el remanente del mes anterior"""
        if self.month > 1:
            previous_book = self.annual_flow.income_books.filter(month=self.month-1).first()
            if previous_book:
                return previous_book.get_month_remnant()
        return 0
    
    def __str__(self):
        return f"Ingresos {self.get_month_display()} {self.annual_flow.year}"

class Income(models.Model):
    book = models.ForeignKey(
        MonthlyIncomeBook,
        on_delete=models.CASCADE,
        related_name='incomes'
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    def get_current_balance(self):
        total_expenses = self.expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0
        return self.amount - total_expenses

    def __str__(self):
        return f"{self.description} - {self.amount}"

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Categoría de Gasto"
        verbose_name_plural = "Categorías de Gastos"
        ordering = ['name']

    def __str__(self):
        return self.name

class Expense(models.Model):
    income = models.ForeignKey(
        Income,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name="Categoría"
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if hasattr(self, 'income') and self.income:
            if self.amount > self.income.get_current_balance() + (self.amount if self.pk else 0):
                raise ValidationError(
                    f'El gasto excede el saldo disponible ({self.income.get_current_balance()})'
                )
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class Remnant(models.Model):
    income_book = models.ForeignKey(
        MonthlyIncomeBook,
        on_delete=models.CASCADE,
        related_name='remnants'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, default='Remanente mensual')
    transfer_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Remanente"
        verbose_name_plural = "Remanentes"
        ordering = ['-transfer_date']
    
    def __str__(self):
        return f"Remanente de {self.income_book} - {self.amount}"

class RemnantWithdrawal(models.Model):
    annual_flow = models.ForeignKey(
        AnnualFlow,
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    withdrawal_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.pk:  # Solo validar si ya existe el objeto
            available_balance = self.annual_flow.get_accumulated_remnant()
            if self.amount > available_balance:
                raise ValidationError(f'El monto excede el saldo disponible (${available_balance})')

    def save(self, *args, **kwargs):
        # Primero guardar para tener el annual_flow asignado
        super().save(*args, **kwargs)
        
        if not hasattr(self, '_processed'):  # Evitar procesamiento múltiple
            # Crear registro negativo en remanentes
            current_month = timezone.now().month
            current_book = self.annual_flow.income_books.get(month=current_month)
            
            Remnant.objects.create(
                income_book=current_book,
                amount=-self.amount,
                description=f'Retiro de remanente: {self.description}'
            )
            
            # Crear ingreso automático
            Income.objects.create(
                book=current_book,
                description=f'Ingreso desde remanentes: {self.description}',
                amount=self.amount
            )
            
            self._processed = True

    class Meta:
        verbose_name = "Retiro de Remanente"
        verbose_name_plural = "Retiros de Remanentes"

    def __str__(self):
        return f"Retiro de remanente: {self.description} - ${self.amount}"

class Presupuesto(models.Model):
    nombre = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)

    def get_total_cost(self):
        return self.items.filter(is_cerrado=False).aggregate(
            total=models.Sum('costo')
        )['total'] or 0

    def __str__(self):
        return self.nombre

class PresupuestoItem(models.Model):
    presupuesto = models.ForeignKey(
        Presupuesto, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    nombre = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    descripcion = models.TextField(blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    is_cerrado = models.BooleanField(default=False)
    export_to = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presupuesto_items'
    )

    def export_to_expense(self, income):
        if not self.is_cerrado:
            expense = Expense.objects.create(
                income=income,
                description=f"Presupuesto: {self.presupuesto.nombre} - {self.nombre}",
                amount=self.costo,
                category=ExpenseCategory.objects.get(name="Presupuestos")
            )
            self.export_to = expense
            self.is_cerrado = True
            self.save()

    def __str__(self):
        return f"{self.presupuesto.nombre} - {self.nombre}"