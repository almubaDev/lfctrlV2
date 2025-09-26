from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy 
from django.db.models import F, Sum, OuterRef, Subquery, DecimalField
from django.db.models.functions import Coalesce
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import (
    AnnualFlow, MonthlyIncomeBook, Income, ExpenseCategory, 
    Expense, Remnant, RemnantWithdrawal, Presupuesto, PresupuestoItem
)
from .forms import (
    AnnualFlowForm, IncomeForm, ExpenseCategoryForm, ExpenseForm, 
    RemnantWithdrawalForm, PresupuestoForm, PresupuestoItemForm
)

# ==================== FLUJOS ANUALES ====================

class AnnualFlowListView(LoginRequiredMixin, ListView):
    model = AnnualFlow
    template_name = 'finances/annual_flow_list.html'
    context_object_name = 'flows'
    ordering = ['-year']

class AnnualFlowDetailView(LoginRequiredMixin, DetailView):
    model = AnnualFlow
    template_name = 'finances/annual_flow_detail.html'
    context_object_name = 'flow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = timezone.now().month
        books = self.object.income_books.all()
        for book in books:
            book.is_current = book.month == current_month
        context['income_books'] = books
        context['closed_month_count'] = books.filter(is_closed=True).count()
        return context

class AnnualFlowCreateView(LoginRequiredMixin, CreateView):
    model = AnnualFlow
    form_class = AnnualFlowForm
    template_name = 'finances/annual_flow_form.html'

    def form_valid(self, form):
        try:
            self.object = form.save()
            self.object.create_monthly_income_books()
            
            books_count = self.object.income_books.count()
            if books_count == 0:
                raise Exception("No se crearon los libros mensuales")
                
            messages.success(self.request, f'Flujo anual {self.object.year} creado con éxito.')
            return redirect('finances:flow-detail', pk=self.object.pk)
            
        except Exception as e:
            messages.error(self.request, f'Error al crear el flujo anual: {str(e)}')
            return redirect('finances:flow-list')

class AnnualFlowDeleteView(LoginRequiredMixin, DeleteView):
    model = AnnualFlow
    template_name = 'finances/confirm_delete.html'
    success_url = reverse_lazy('finances:flow-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Flujo anual eliminado con éxito.')
        return super().delete(request, *args, **kwargs)

# ==================== LIBROS MENSUALES ====================

class MonthlyBookDetailView(LoginRequiredMixin, DetailView):
    model = MonthlyIncomeBook
    template_name = 'finances/monthly_book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incomes = self.object.incomes.all().order_by('-date')
        
        total_month_incomes = 0
        total_month_expenses = 0
        
        for income in incomes:
            total_expenses = income.expenses.aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            total_month_incomes += income.amount
            total_month_expenses += total_expenses
            
            income.total_expenses = total_expenses
            income.current_balance = income.get_current_balance()
            income.expenses_count = income.expenses.count()
        
        context['incomes'] = incomes
        context['total_month_incomes'] = total_month_incomes
        context['total_month_expenses'] = total_month_expenses
        context['month_balance'] = total_month_incomes - total_month_expenses
        return context

@login_required
def close_month(request, book_id):
    book = get_object_or_404(MonthlyIncomeBook, id=book_id)
    
    if request.method == 'POST':
        try:
            if book.is_closed:
                messages.error(request, 'Este mes ya está cerrado.')
                return redirect('finances:monthly-book-detail', pk=book_id)
            
            total_income = book.incomes.aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            total_expenses = Expense.objects.filter(
                income__book=book
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            remaining = total_income - total_expenses
            
            if remaining > 0:
                Remnant.objects.create(
                    income_book=book,
                    amount=remaining,
                    description=f'Remanente de {book.get_month_display()} {book.annual_flow.year}'
                )
            
            book.is_closed = True
            book.save()
            
            all_months_closed = all(
                book.annual_flow.income_books.values_list('is_closed', flat=True)
            )
            
            if all_months_closed:
                book.annual_flow.close_year()
                
            messages.success(request, f'Mes cerrado exitosamente. Remanente: ${remaining:,.0f}')
            
            referer = request.META.get('HTTP_REFERER', '')
            if 'flow-detail' in referer:
                return redirect('finances:flow-detail', pk=book.annual_flow.pk)
            else:
                return redirect('finances:monthly-book-detail', pk=book_id)
            
        except Exception as e:
            messages.error(request, f'Error al cerrar el mes: {str(e)}')
            return redirect('finances:monthly-book-detail', pk=book_id)
    
    return redirect('finances:monthly-book-detail', pk=book_id)

# ==================== INGRESOS ====================

@login_required
def add_income(request, book_id):
    book = get_object_or_404(MonthlyIncomeBook, id=book_id)
    
    if book.is_closed:
        messages.error(request, 'No se pueden agregar ingresos a un mes cerrado.')
        return redirect('finances:monthly-book-detail', pk=book_id)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.book = book
            income.save()
            messages.success(request, 'Ingreso registrado exitosamente.')
            return redirect('finances:monthly-book-detail', pk=book_id)
    else:
        form = IncomeForm()

    return render(request, 'finances/income_form.html', {
        'form': form,
        'book': book
    })

class IncomeDetailView(LoginRequiredMixin, DetailView):
    model = Income
    template_name = 'finances/income_detail.html'
    context_object_name = 'income'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expenses = self.object.expenses.all()
        expenses_by_category = {}
        
        for expense in expenses:
            category = expense.category
            if category not in expenses_by_category:
                expenses_by_category[category] = {
                    'total': 0,
                    'expenses': []
                }
            expenses_by_category[category]['expenses'].append(expense)
            expenses_by_category[category]['total'] += expense.amount
        
        context['expenses_by_category'] = expenses_by_category
        context['total_expenses'] = sum(cat_data['total'] for cat_data in expenses_by_category.values())
        context['current_balance'] = self.object.get_current_balance()
        
        return context

class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'finances/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('finances:monthly-book-detail', 
                          kwargs={'pk': self.object.book.id})

    def delete(self, request, *args, **kwargs):
        if self.get_object().expenses.exists():
            messages.error(request, 'No se puede eliminar un ingreso que tiene gastos asociados.')
            return redirect('finances:income-detail', pk=self.get_object().id)
        messages.success(request, 'Ingreso eliminado con éxito.')
        return super().delete(request, *args, **kwargs)

# ==================== CATEGORÍAS DE GASTOS ====================

class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = 'finances/category_list.html'
    context_object_name = 'categories'

class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'finances/category_form.html'
    success_url = reverse_lazy('finances:category-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Categoría creada exitosamente.')
        return response

class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'finances/category_form.html'
    success_url = reverse_lazy('finances:category-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return response

class ExpenseCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenseCategory
    template_name = 'finances/confirm_delete.html'
    success_url = reverse_lazy('finances:category-list')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, 'Categoría eliminada exitosamente.')
            return response
        except models.ProtectedError:
            messages.error(request, 'No se puede eliminar una categoría que tiene gastos asociados.')
            return redirect('finances:category-list')

# ==================== GASTOS ====================

@login_required
def add_expense(request, income_id):
    income = get_object_or_404(Income, id=income_id)
    
    if income.book.is_closed:
        messages.error(request, 'No se pueden agregar gastos a un ingreso de un mes cerrado.')
        return redirect('finances:income-detail', pk=income_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.income = income
            
            if expense.amount > income.get_current_balance():
                messages.error(
                    request, 
                    f'El gasto (${expense.amount}) excede el saldo disponible (${income.get_current_balance()})'
                )
            else:
                expense.save()
                messages.success(request, 'Gasto registrado exitosamente.')
                return redirect('finances:income-detail', pk=income_id)
    else:
        form = ExpenseForm()

    return render(request, 'finances/expense_form.html', {
        'form': form,
        'income': income,
        'available_balance': income.get_current_balance()
    })

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, id=pk)
    income_id = expense.income.id
    
    if expense.income.book.is_closed:
        messages.error(request, 'No se pueden eliminar gastos de un mes cerrado.')
        return redirect('finances:income-detail', pk=income_id)
    
    expense.delete()
    messages.success(request, 'Gasto eliminado exitosamente.')
    return redirect('finances:income-detail', pk=income_id)

# ==================== REMANENTES ====================

class RemnantListView(LoginRequiredMixin, ListView):
    model = Remnant
    template_name = 'finances/remnant_list.html'
    context_object_name = 'remnants'
    ordering = ['-transfer_date']

    def get_queryset(self):
        flow_id = self.kwargs.get('flow_id')
        queryset = super().get_queryset()
        if flow_id:
            queryset = queryset.filter(income_book__annual_flow_id=flow_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flow_id = self.kwargs.get('flow_id')
        if flow_id:
            context['annual_flow'] = AnnualFlow.objects.get(pk=flow_id)
        context['total_remnants'] = self.get_queryset().aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return context

@login_required
def remnant_detail(request, remnant_id):
    remnant = get_object_or_404(Remnant, id=remnant_id)
    return render(request, 'finances/remnant_detail.html', {
        'remnant': remnant,
        'income_book': remnant.income_book
    })

@login_required
def withdraw_remnant(request, flow_id):
    flow = get_object_or_404(AnnualFlow, id=flow_id)
    available_balance = flow.get_accumulated_remnant()

    if request.method == 'POST':
        form = RemnantWithdrawalForm(request.POST)
        if form.is_valid():
            try:
                withdrawal = form.save(commit=False)
                withdrawal.annual_flow_id = flow_id
                
                if withdrawal.amount > available_balance:
                    messages.error(
                        request, 
                        f'El monto excede el saldo disponible (${available_balance:,.0f})'
                    )
                else:
                    withdrawal.full_clean()
                    withdrawal.save()
                    messages.success(
                        request, 
                        f'Retiro de remanente por ${withdrawal.amount:,.0f} procesado exitosamente'
                    )
                    return redirect('finances:remnant-list')
            except Exception as e:
                messages.error(request, f'Error al procesar el retiro: {str(e)}')
    else:
        form = RemnantWithdrawalForm()

    return render(request, 'finances/remnant_withdrawal_form.html', {
        'form': form,
        'flow': flow,
        'available_balance': available_balance
    })

# ==================== REPORTES ====================

@login_required
def annual_report(request, flow_id):
    flow = get_object_or_404(AnnualFlow, id=flow_id)
    months_names = dict(MonthlyIncomeBook.MONTH_CHOICES)
    
    expenses_by_category = {}
    monthly_totals = {}
    
    for book in flow.income_books.all():
        monthly_totals[book.month] = {
            'name': months_names[book.month],
            'incomes': book.get_total_income(),
            'expenses': book.get_total_expenses()
        }
        
        expenses = Expense.objects.filter(income__book=book)
        for expense in expenses:
            if expense.category not in expenses_by_category:
                expenses_by_category[expense.category] = {
                    'monthly': {m: 0 for m in range(1, 13)},
                    'total': 0
                }
            expenses_by_category[expense.category]['monthly'][book.month] += expense.amount
            expenses_by_category[expense.category]['total'] += expense.amount

    incomes = []
    for book in flow.income_books.all():
        for income in book.incomes.all():
            income_expenses = {}
            for expense in income.expenses.all():
                if expense.category not in income_expenses:
                    income_expenses[expense.category] = 0
                income_expenses[expense.category] += expense.amount
            
            incomes.append({
                'month': book.get_month_display(),
                'description': income.description,
                'amount': income.amount,
                'expenses': income_expenses,
                'total_expenses': sum(income_expenses.values())
            })

    return render(request, 'finances/annual_report.html', {
        'flow': flow,
        'months_names': months_names,
        'incomes': incomes,
        'expenses_by_category': expenses_by_category,
        'monthly_totals': monthly_totals,
        'total_income': flow.get_total_income(),
        'total_expenses': flow.get_total_expenses()
    })

# ==================== PRESUPUESTOS ====================

class PresupuestoListView(LoginRequiredMixin, ListView):
    model = Presupuesto
    template_name = 'finances/presupuesto_list.html'
    context_object_name = 'presupuestos'

class PresupuestoDetailView(LoginRequiredMixin, DetailView):
    model = Presupuesto
    template_name = 'finances/presupuesto_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_cost = self.object.get_total_cost()
        
        available_incomes = Income.objects.filter(
            book__is_closed=False
        ).select_related('book')
        
        total_available = sum(
            income.get_current_balance() 
            for income in available_incomes
        )
        
        context.update({
            'items': self.object.items.all(),
            'total_cost': total_cost,
            'incomes': available_incomes if total_available >= total_cost else [],
            'insufficient_funds': total_available < total_cost
        })
        
        return context

class PresupuestoCreateView(LoginRequiredMixin, CreateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = 'finances/presupuesto_form.html'
    success_url = reverse_lazy('finances:presupuesto-list')

class PresupuestoDeleteView(LoginRequiredMixin, DeleteView):
    model = Presupuesto
    template_name = 'finances/confirm_delete.html'
    success_url = reverse_lazy('finances:presupuesto-list')

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except models.ProtectedError:
            messages.error(request, 'No se puede eliminar un presupuesto con items exportados')
            return redirect('finances:presupuesto-list')

@login_required
def add_presupuesto_item(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    
    if request.method == 'POST':
        form = PresupuestoItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.presupuesto = presupuesto
            item.save()
            return redirect('finances:presupuesto-detail', pk=presupuesto_id)
    else:
        form = PresupuestoItemForm()
    
    return render(request, 'finances/presupuesto_item_form.html', {
        'form': form,
        'presupuesto': presupuesto
    })

class PresupuestoItemUpdateView(LoginRequiredMixin, UpdateView):
    model = PresupuestoItem
    form_class = PresupuestoItemForm
    template_name = 'finances/presupuesto_item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presupuesto'] = self.object.presupuesto
        return context

    def get_success_url(self):
        return reverse_lazy('finances:presupuesto-detail', kwargs={'pk': self.object.presupuesto.id})

@login_required
def delete_presupuesto_item(request, pk):
    item = get_object_or_404(PresupuestoItem, pk=pk)
    presupuesto_id = item.presupuesto.id
    
    if item.is_cerrado:
        messages.error(request, 'No se puede eliminar un item exportado')
    else:
        item.delete()
        messages.success(request, 'Item eliminado exitosamente')
    
    return redirect('finances:presupuesto-detail', pk=presupuesto_id)

@login_required
def export_to_expense(request, item_id, income_ids):
    item = get_object_or_404(PresupuestoItem, id=item_id)
    remaining_amount = item.costo
    income_list = Income.objects.filter(id__in=income_ids.split(','))
    
    presupuestos_cat, _ = ExpenseCategory.objects.get_or_create(
        name='Presupuestos',
        defaults={'description': 'Gastos asociados a presupuestos'}
    )

    try:
        expenses_created = []
        for income in income_list:
            available_balance = income.get_current_balance()
            if available_balance <= 0:
                continue

            amount_to_deduct = min(remaining_amount, available_balance)
            
            if amount_to_deduct > 0:
                expense = Expense.objects.create(
                    income=income,
                    category=presupuestos_cat,
                    description=f"Presupuesto: {item.presupuesto.nombre} - {item.nombre}",
                    amount=amount_to_deduct
                )
                expenses_created.append(expense)
                remaining_amount -= amount_to_deduct

            if remaining_amount <= 0:
                break

        if remaining_amount <= 0:
            item.is_cerrado = True
            item.export_to = expenses_created[0]
            item.save()
            messages.success(request, 'Item exportado exitosamente')
        else:
            for expense in expenses_created:
                expense.delete()
            messages.error(request, f'Saldo insuficiente. Faltan ${remaining_amount}')
            
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('finances:presupuesto-detail', pk=item.presupuesto.id)