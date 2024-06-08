from django.urls import path
from . import views

urlpatterns = [
    path('month/', views.expense_month, name='expense_month'),
    path('weekly/', views.weekly, name='weekly'),
    path('year/', views.info_year, name='info_year'),
]
