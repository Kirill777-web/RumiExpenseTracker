import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from expenses.models import AddMoneyInfo


def expense_month(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney = AddMoneyInfo.objects.filter(
            user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
        finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category

        Category_list = list(set(map(get_Category, addmoney)))

        def get_expense_category_amount(Category, add_money):
            quantity = 0
            filtered_by_category = addmoney.filter(
                Category=Category, add_money="Expense")
            for item in filtered_by_category:
                quantity += item.quantity
            return quantity

        for x in addmoney:
            for y in Category_list:
                finalrep[y] = get_expense_category_amount(y, "Expense")

        return JsonResponse({'expense_category_data': finalrep}, safe=False)
    return JsonResponse({'error': 'Unauthorized'}, status=401)


def weekly(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_week_ago = todays_date - datetime.timedelta(days=7)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
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
    return redirect('home')


def info_year(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_year_ago = todays_date - datetime.timedelta(days=365)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney = AddMoneyInfo.objects.filter(
            user=user1, Date__gte=one_year_ago, Date__lte=todays_date)
        finalrep = {}

        def get_Category(addmoney_info):
            return addmoney_info.Category

        Category_list = list(set(map(get_Category, addmoney)))

        def get_expense_category_amount(Category, add_money):
            quantity = 0
            filtered_by_category = addmoney.filter(
                Category=Category, add_money="Expense")
            for item in filtered_by_category:
                quantity += item.quantity
            return quantity

        for x in addmoney:
            for y in Category_list:
                finalrep[y] = get_expense_category_amount(y, "Expense")

        return JsonResponse({'expense_category_data': finalrep}, safe=False)
    return JsonResponse({'error': 'Unauthorized'}, status=401)
