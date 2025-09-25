from django.contrib import admin
from .models import (
    AnnualFlow, MonthlyIncomeBook, Income, ExpenseCategory, 
    Expense, Remnant, RemnantWithdrawal, Presupuesto, PresupuestoItem
)

@admin.register(AnnualFlow)
class AnnualFlowAdmin(admin.ModelAdmin):
    list_display = ['year', 'created_at', 'is_closed']
    list_filter = ['is_closed']
    
@admin.register(MonthlyIncomeBook)
class MonthlyIncomeBookAdmin(admin.ModelAdmin):
    list_display = ['annual_flow', 'month', 'is_closed']
    list_filter = ['is_closed', 'annual_flow__year']
    
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'book', 'date']
    list_filter = ['book__annual_flow__year', 'book__month']
    search_fields = ['description']
    
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'category', 'income', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description']
    
@admin.register(Remnant)
class RemnantAdmin(admin.ModelAdmin):
    list_display = ['income_book', 'amount', 'description', 'transfer_date']
    list_filter = ['income_book__annual_flow__year']
    
@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'created_at', 'is_closed']
    
@admin.register(PresupuestoItem)
class PresupuestoItemAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'presupuesto', 'costo', 'is_cerrado']
    list_filter = ['is_cerrado', 'presupuesto']