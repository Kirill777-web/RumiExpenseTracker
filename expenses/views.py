import json
import pytz
import calendar
import datetime
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import UserProfile
from .models import AddMoneyInfo


from django.db.models import Sum, F, Value
from django.db.models.functions import Lower, Trim


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

    # Clean up and aggregate categories
    categories = addmoney_info.annotate(
        cleaned_category=Lower(Trim(F('Category')))
    ).values('cleaned_category').annotate(
        total_quantity=Sum('quantity')
    ).order_by('cleaned_category')

    category_labels = [category['cleaned_category'] for category in categories]
    category_data = [category['total_quantity'] for category in categories]

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
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            description = request.POST.get("description", "No description")
            Date = timezone.make_aware(datetime.datetime.strptime(
                request.POST["Date"], '%Y-%m-%d'))
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
        # Ensure the date is timezone-aware
        add.Date = timezone.make_aware(
            datetime.datetime.strptime(request.POST["Date"], '%Y-%m-%d'))
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

    # Prepare data for the pie chart
    finalrep = {}
    for item in addmoney:
        category = item.Category
        if category not in finalrep:
            finalrep[category] = {'expense': 0, 'income': 0}
        if item.add_money == 'Expense':
            finalrep[category]['expense'] += item.quantity
        else:
            finalrep[category]['income'] += item.quantity

    # Prepare data for the line chart (daily data for the last 30 days)
    daily_data = []
    for i in range(30):
        date = timezone.now().date() - datetime.timedelta(days=i)
        daily_expense = sum(item.quantity for item in addmoney if item.Date.date(
        ) == date and item.add_money == 'Expense')
        daily_income = sum(item.quantity for item in addmoney if item.Date.date(
        ) == date and item.add_money == 'Income')
        daily_data.append({'date': date.strftime('%Y-%m-%d'),
                          'expense': daily_expense, 'income': daily_income})
    daily_data.reverse()

    # Prepare data for the donut chart (savings distribution)
    savings_data = {'Saved': user1.userprofile.savings}
    for item in addmoney:
        if item.add_money == 'Expense':
            if 'Spent' in savings_data:
                savings_data['Spent'] += item.quantity
            else:
                savings_data['Spent'] = item.quantity

    # Prepare data for the histogram (expense frequency)
    expense_amounts = [
        item.quantity for item in addmoney if item.add_money == 'Expense']
    histogram_data = {
        'labels': ['0-50', '51-100', '101-150', '151-200', '201-250', '251-300', '301-350', '351-400'],
        'values': [0] * 8
    }
    for amount in expense_amounts:
        if amount <= 50:
            histogram_data['values'][0] += 1
        elif amount <= 100:
            histogram_data['values'][1] += 1
        elif amount <= 150:
            histogram_data['values'][2] += 1
        elif amount <= 200:
            histogram_data['values'][3] += 1
        elif amount <= 250:
            histogram_data['values'][4] += 1
        elif amount <= 300:
            histogram_data['values'][5] += 1
        elif amount <= 350:
            histogram_data['values'][6] += 1
        else:
            histogram_data['values'][7] += 1

    context = {
        'expense_category_data': json.dumps(finalrep),
        'daily_data': json.dumps(daily_data),
        'savings_data': json.dumps(savings_data),
        'histogram_data': json.dumps(histogram_data),
        'todays_date': timezone.now().strftime('%Y-%m-%d')
    }

    return render(request, 'expenses/charts.html', context)


@login_required
def stats(request):
    user1 = request.user

    todays_date = timezone.now().date()  # Use timezone-aware now
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
        item.quantity for item in expenses if item.add_money == 'Expense')
    total_income = sum(
        item.quantity for item in expenses if item.add_money == 'Income')
    remaining_savings = (user_profile.savings or 0) + \
        total_income - total_expenses
    over_budget = max(0, total_expenses - (user_profile.savings or 0))

    # Data for expense category chart
    categories = expenses.values('Category').distinct()
    category_labels = [category['Category'] for category in categories]
    category_data = [sum(item.quantity for item in expenses if item.Category == category)
                     for category in category_labels]

    # Data for monthly expenses and income chart
    monthly_expenses = [0] * 12
    monthly_income = [0] * 12
    today = datetime.date.today()
    current_year = today.year
    for item in expenses:
        if item.Date.year == current_year:
            month_index = item.Date.month - 1
            if item.add_money == 'Expense':
                monthly_expenses[month_index] += item.quantity
            else:
                monthly_income[month_index] += item.quantity

    monthly_labels = [calendar.month_name[i] for i in range(1, 13)]

    # Calculate top expense categories
    top_expense_categories = sorted(
        zip(category_labels, category_data), key=lambda x: x[1], reverse=True)[:5]

    context = {
        'total_expenses': total_expenses,
        'total_income': total_income,
        'remaining_savings': remaining_savings,
        'over_budget': over_budget,
        'expenses': expenses,
        'category_labels': category_labels,
        'category_data': category_data,
        'monthly_labels': monthly_labels,
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'top_expense_categories': top_expense_categories,
    }

    return render(request, 'expenses/stats.html', context)


@login_required
def tables(request):
    user = request.user
    expenses = AddMoneyInfo.objects.filter(user=user).order_by('-Date')
    context = {'expenses': expenses}
    return render(request, 'expenses/tables.html', context)
