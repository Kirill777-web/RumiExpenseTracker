from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('add/', views.addmoney, name='addmoney'),
    path('add/submit/', views.addmoney_submission, name='addmoney_submission'),
    path('edit/<int:id>/', views.expense_edit, name='expense_edit'),
    path('delete/<int:id>/', views.expense_delete, name='expense_delete'),
    path('update/<int:id>/', views.addmoney_update, name='addmoney_update'),
    path('search/', views.search, name='search'),
    path('charts/', views.charts, name='charts'),
    path('stats/', views.stats, name='stats'),
    path('tables/', views.tables, name='tables'),  # Ensure this line exists
]
