import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import UserProfile
from .models import AddMoneyInfo


@login_required
def index(request):
    user1 = request.user
    addmoney_info = AddMoneyInfo.objects.filter(user=user1).order_by('-Date')
    paginator = Paginator(addmoney_info, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_income = sum(
        item.quantity for item in addmoney_info if item.add_money == 'Income')
    total_expenses = sum(
        item.quantity for item in addmoney_info if item.add_money == 'Expense')
    remaining_balance = total_income - total_expenses

    categories = addmoney_info.values('Category').distinct()
    category_labels = [category['Category'] for category in categories]
    category_data = [sum(item.quantity for item in addmoney_info if item.Category == category)
                     for category in category_labels]

    context = {
        'page_obj': page_obj,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'category_labels': category_labels,
        'category_data': category_data,
    }

    return render(request, 'expenses/index.html', context)


@login_required
def addmoney(request):
    categories = ["Food", "Transport", "Entertainment",
                  "Health", "Other", "Shopping", "Rent", "Bills", "Salary"]
    return render(request, 'expenses/addmoney.html', {'categories': categories})


@login_required
def addmoney_submission(request):
    if request.method == "POST":
        user1 = request.user
        add_money = request.POST["add_money"]
        quantity = request.POST["quantity"]
        description = request.POST.get("description", "No description")
        Date = request.POST["Date"]
        Category = request.POST["Category"]
        add = AddMoneyInfo(user=user1, add_money=add_money, quantity=quantity,
                           description=description, Date=Date, Category=Category)
        add.save()
        return redirect('index')
    return redirect('home')


@login_required
def addmoney_update(request, id):
    add = get_object_or_404(AddMoneyInfo, id=id, user=request.user)
    categories = ["Food", "Transport", "Entertainment",
                  "Health", "Other", "Shopping", "Rent", "Bills"]
    if request.method == "POST":
        add.add_money = request.POST["add_money"]
        add.quantity = request.POST["quantity"]
        add.description = request.POST.get("description", "No description")
        add.Date = request.POST["Date"]
        add.Category = request.POST["Category"]
        add.save()
        return redirect('index')
    else:
        context = {
            'add_money': add.add_money,
            'quantity': add.quantity,
            'description': add.description,
            'Date': add.Date,
            'Category': add.Category,
            'id': id,
            'categories': categories
        }
        return render(request, 'expenses/addmoney.html', context)


@login_required
def expense_edit(request, id):
    addmoney_info = get_object_or_404(AddMoneyInfo, id=id, user=request.user)
    return render(request, 'expenses/expense_edit.html', {'addmoney_info': addmoney_info})


@login_required
def expense_delete(request, id):
    addmoney_info = get_object_or_404(AddMoneyInfo, id=id, user=request.user)
    addmoney_info.delete()
    return redirect('index')


@login_required
def search(request):
    query = request.GET.get('q')
    if query:
        results = AddMoneyInfo.objects.filter(
            description__icontains=query, user=request.user)
    else:
        results = AddMoneyInfo.objects.none()
    context = {'results': results}
    return render(request, 'expenses/search.html', context)


@login_required
def charts(request):
    user1 = request.user

    addmoney = AddMoneyInfo.objects.filter(user=user1)
    finalrep = {}
    for item in addmoney:
        category = item.Category
        if category not in finalrep:
            finalrep[category] = {'expense': 0, 'income': 0}
        if item.add_money == 'Expense':
            finalrep[category]['expense'] += item.quantity
        else:
            finalrep[category]['income'] += item.quantity

    monthly_expense = [0] * 12
    monthly_income = [0] * 12
    today = datetime.date.today()
    current_year = today.year
    for item in addmoney:
        if item.Date.year == current_year:
            month_index = item.Date.month - 1
            if item.add_money == 'Expense':
                monthly_expense[month_index] += item.quantity
            else:
                monthly_income[month_index] += item.quantity

    context = {
        'expense_category_data': finalrep,
        'monthly_expense': monthly_expense,
        'monthly_income': monthly_income
    }
    return render(request, 'expenses/charts.html', context)


@login_required
def stats(request):
    user1 = request.user

    todays_date = datetime.date.today()
    one_month_ago = todays_date - datetime.timedelta(days=30)

    try:
        user_profile = user1.userprofile
    except UserProfile.DoesNotExist:
        messages.error(
            request, 'User profile not found. Please create your profile.')
        return redirect('profile')

    expenses = AddMoneyInfo.objects.filter(
        user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
    total_expenses = sum(
        expense.quantity for expense in expenses if expense.add_money == 'Expense')
    total_income = sum(
        income.quantity for income in expenses if income.add_money == 'Income')
    remaining_savings = user_profile.savings + total_income - total_expenses
    over_budget = max(0, total_expenses - user_profile.savings)

    context = {
        'total_expenses': total_expenses,
        'total_income': total_income,
        'remaining_savings': remaining_savings,
        'over_budget': over_budget,
        'expenses': expenses,
    }
    return render(request, 'expenses/stats.html', context)


@login_required
def tables(request):
    user = request.user
    expenses = AddMoneyInfo.objects.filter(user=user).order_by('-Date')
    context = {'expenses': expenses}
    return render(request, 'expenses/tables.html', context)
