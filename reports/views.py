import json
import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from expenses.models import AddMoneyInfo


@login_required
def info_year(request):
    user1 = request.user

    todays_date = timezone.now().date()  # Use timezone-aware now
    start_of_year = datetime.date(todays_date.year, 1, 1)
    end_of_year = datetime.date(todays_date.year, 12, 31)

    addmoney = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=start_of_year, Date__lte=end_of_year)

    months = [start_of_year + datetime.timedelta(days=i*30) for i in range(12)]
    month_labels = [month.strftime('%B') for month in months]

    finalrep = {month.strftime('%B'): {'expense': 0, 'income': 0}
                for month in months}

    for item in addmoney:
        month = item.Date.strftime('%B')
        if item.add_money == 'Expense':
            finalrep[month]['expense'] += item.quantity
        else:
            finalrep[month]['income'] += item.quantity

    context = {
        'expense_category_data': json.dumps(finalrep),
        'month_labels': json.dumps(month_labels),
        'todays_date': todays_date.strftime('%Y')
    }

    return render(request, 'reports/yearly_report.html', context)


@login_required
def expense_month(request):
    user1 = request.user

    todays_date = timezone.now().date()  # Use timezone-aware now
    first_day_of_month = todays_date.replace(day=1)
    last_day_of_month = (first_day_of_month + datetime.timedelta(days=32)
                         ).replace(day=1) - datetime.timedelta(days=1)
    days_in_month = (last_day_of_month - first_day_of_month).days + 1

    days = [first_day_of_month +
            datetime.timedelta(days=i) for i in range(days_in_month)]

    addmoney = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=first_day_of_month, Date__lte=last_day_of_month)

    finalrep = {}

    for day in days:
        day_str = day.strftime('%Y-%m-%d')
        finalrep[day_str] = {
            'expense': sum(item.quantity for item in addmoney if item.add_money == 'Expense' and item.Date.date() == day),
            'income': sum(item.quantity for item in addmoney if item.add_money == 'Income' and item.Date.date() == day)
        }

    context = {
        'expense_category_data': json.dumps(finalrep),
        'todays_date': todays_date.strftime('%B %Y'),
        'days': json.dumps([day.strftime('%Y-%m-%d') for day in days])
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
