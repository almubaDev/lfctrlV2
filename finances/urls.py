from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    # Flujos Anuales
    path('', 
         views.AnnualFlowListView.as_view(), 
         name='flow-list'),
    path('flow/<int:pk>/',
         views.AnnualFlowDetailView.as_view(),
         name='flow-detail'),
    path('nuevo/', 
         views.AnnualFlowCreateView.as_view(), 
         name='flow-create'),
    path('<int:pk>/eliminar/', 
         views.AnnualFlowDeleteView.as_view(), 
         name='flow-delete'),
    
    # Libros Mensuales
    path('monthly/<int:pk>/', 
         views.MonthlyBookDetailView.as_view(), 
         name='monthly-book-detail'),
    path('monthly/<int:book_id>/close/',
         views.close_month,
         name='close-month'),
    
    # Ingresos
    path('monthly/<int:book_id>/add-income/',
         views.add_income,
         name='add-income'),
    path('income/<int:pk>/',
         views.IncomeDetailView.as_view(),
         name='income-detail'),
    path('income/<int:pk>/eliminar/',
         views.IncomeDeleteView.as_view(),
         name='income-delete'),
    
    # Categorías de Gastos
    path('categories/',
         views.ExpenseCategoryListView.as_view(),
         name='category-list'),
    path('categories/new/',
         views.ExpenseCategoryCreateView.as_view(),
         name='category-create'),
    path('categories/<int:pk>/edit/',
         views.ExpenseCategoryUpdateView.as_view(),
         name='category-edit'),
    path('categories/<int:pk>/delete/',
         views.ExpenseCategoryDeleteView.as_view(),
         name='category-delete'),
    
    # Gastos
    path('income/<int:income_id>/add-expense/',
         views.add_expense,
         name='add-expense'),
    path('expense/<int:pk>/delete/',
         views.delete_expense,
         name='delete-expense'),
    
    # Remanentes
    path('remnants/', 
         views.RemnantListView.as_view(), 
         name='remnant-list'),
    path('flow/<int:flow_id>/remnants/', 
         views.RemnantListView.as_view(), 
         name='flow-remnants'),
    path('remnant/<int:remnant_id>/', 
         views.remnant_detail, 
         name='remnant-detail'),
    path('flow/<int:flow_id>/withdraw/', 
         views.withdraw_remnant, 
         name='withdraw-remnant'),
    
    # Report
    path('flow/<int:flow_id>/report/', 
         views.annual_report, 
         name='annual-report'),
    
    # Presupuesto
    path('presupuestos/', 
         views.PresupuestoListView.as_view(), 
         name='presupuesto-list'),
    
    path('presupuestos/nuevo/', 
         views.PresupuestoCreateView.as_view(), 
         name='presupuesto-create'),
    
    path('presupuestos/<int:pk>/', 
         views.PresupuestoDetailView.as_view(), 
         name='presupuesto-detail'),
    
    path('presupuestos/<int:presupuesto_id>/add-item/',
         views.add_presupuesto_item,
         name='add-presupuesto-item'),
    
    path('presupuesto-item/<int:item_id>/export/<str:income_ids>/',
         views.export_to_expense,
         name='export-presupuesto-item'),
    
    path('presupuestos/<int:pk>/delete/', 
         views.PresupuestoDeleteView.as_view(), 
         name='presupuesto-delete'),
    
    path('presupuesto-item/<int:pk>/edit/',
         views.PresupuestoItemUpdateView.as_view(),
         name='edit-presupuesto-item'),
    
    path('presupuesto-item/<int:pk>/delete/',
         views.delete_presupuesto_item,
         name='delete-presupuesto-item'),
]