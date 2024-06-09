import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from expenses.models import AddMoneyInfo


@login_required
def info_year(request):
    user1 = request.user

    todays_date = datetime.date.today()
    one_year_ago = todays_date - datetime.timedelta(days=365)
    addmoney = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=one_year_ago, Date__lte=todays_date)
    finalrep = {}

    def get_Category(addmoney_info):
        return addmoney_info.Category

    Category_list = list(set(map(get_Category, addmoney)))

    def get_category_amount(Category, add_money):
        quantity = 0
        filtered_by_category = addmoney.filter(
            Category=Category, add_money=add_money)
        for item in filtered_by_category:
            quantity += item.quantity
        return quantity

    for y in Category_list:
        finalrep[y] = {
            'expense': get_category_amount(y, "Expense"),
            'income': get_category_amount(y, "Income")
        }

    return render(request, 'reports/yearly_report.html', {'expense_category_data': finalrep})


@login_required
def expense_month(request):
    user1 = request.user

    todays_date = datetime.date.today()
    one_month_ago = todays_date - datetime.timedelta(days=30)
    addmoney = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
    finalrep = {}

    def get_Category(addmoney_info):
        return addmoney_info.Category

    Category_list = list(set(map(get_Category, addmoney)))

    def get_category_amount(Category, add_money):
        quantity = 0
        filtered_by_category = addmoney.filter(
            Category=Category, add_money=add_money)
        for item in filtered_by_category:
            quantity += item.quantity
        return quantity

    for y in Category_list:
        finalrep[y] = {
            'expense': get_category_amount(y, "Expense"),
            'income': get_category_amount(y, "Income")
        }

    context = {
        'expense_category_data': finalrep,
        'todays_date': todays_date.strftime('%B %Y')
    }
    return render(request, 'reports/monthly_report.html', context)


@login_required
def weekly(request):
    user1 = request.user

    todays_date = datetime.date.today()
    one_week_ago = todays_date - datetime.timedelta(days=7)
    addmoney_info = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=one_week_ago, Date__lte=todays_date)
    sum_expenses = sum(
        item.quantity for item in addmoney_info if item.add_money == 'Expense')
    sum_income = sum(
        item.quantity for item in addmoney_info if item.add_money == 'Income')

    context = {
        'sum_expenses': sum_expenses,
        'sum_income': sum_income,
        'addmoney_info': addmoney_info
    }
    return render(request, 'reports/weekly_report.html', context)
