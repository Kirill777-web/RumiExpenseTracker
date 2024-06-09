import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import UserProfile
from .models import AddMoneyInfo


def index(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        addmoney_info = AddMoneyInfo.objects.filter(
            user=user1).order_by('-Date')
        paginator = Paginator(addmoney_info, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Calculate statistics
        total_income = sum(
            item.quantity for item in addmoney_info if item.add_money == 'Income')
        total_expenses = sum(
            item.quantity for item in addmoney_info if item.add_money == 'Expense')
        remaining_balance = total_income - total_expenses

        # Prepare data for category breakdown
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
    return redirect('home')


def addmoney(request):
    categories = ["Food", "Transport", "Entertainment",
                  "Health", "Other", "Shopping", "Rent", "Bills", "Salary"]
    return render(request, 'expenses/addmoney.html', {'categories': categories})


def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            # Use get() to handle missing data
            description = request.POST.get("description", "No description")
            Date = request.POST["Date"]
            Category = request.POST["Category"]
            add = AddMoneyInfo(user=user1, add_money=add_money, quantity=quantity,
                               description=description, Date=Date, Category=Category)
            add.save()
            return redirect('index')
    return redirect('home')


def addmoney_update(request, id):
    if request.session.has_key('is_logged'):
        categories = ["Food", "Transport", "Entertainment",
                      "Health", "Other", "Shopping", "Rent", "Bills"]
        if request.method == "POST":
            add = AddMoneyInfo.objects.get(id=id)
            add.add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            # Use get() to handle missing data
            add.description = request.POST.get("description", "No description")
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add.save()
            return redirect('index')
        else:
            add = AddMoneyInfo.objects.get(id=id)
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
    return redirect('home')


def expense_edit(request, id):
    if request.session.has_key('is_logged'):
        addmoney_info = AddMoneyInfo.objects.get(id=id)
        return render(request, 'expenses/expense_edit.html', {'addmoney_info': addmoney_info})
    return redirect('home')


def expense_delete(request, id):
    if request.session.has_key('is_logged'):
        addmoney_info = AddMoneyInfo.objects.get(id=id)
        addmoney_info.delete()
        return redirect('index')
    return redirect('home')


def search(request):
    query = request.GET.get('q')
    if query:
        results = AddMoneyInfo.objects.filter(description__icontains=query)
    else:
        results = AddMoneyInfo.objects.none()
    context = {'results': results}
    return render(request, 'expenses/search.html', context)


@login_required
def charts(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        # Get expense and income data for the pie chart
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

        # Prepare data for the bar chart (monthly trend)
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
    return JsonResponse({'error': 'Unauthorized'}, status=401)


@login_required
def stats(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        # Ensure the user has a profile
        try:
            user_profile = user1.userprofile
        except UserProfile.DoesNotExist:
            messages.error(
                request, 'User profile not found. Please create your profile.')
            return redirect('profile')

        # Handle None values
        savings = user_profile.savings if user_profile.savings is not None else 0
        income = user_profile.income if user_profile.income is not None else 0

        addmoney_info = AddMoneyInfo.objects.filter(
            user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
        sum_expense = 0
        sum_income = 0
        for item in addmoney_info:
            if item.add_money == 'Expense':
                sum_expense += item.quantity
            elif item.add_money == 'Income':
                sum_income += item.quantity

        remaining_savings = savings + sum_income - sum_expense
        amount_over_budget = remaining_savings if remaining_savings < 0 else 0
        remaining_savings = max(remaining_savings, 0)

        context = {
            'total_expenses': sum_expense,
            'total_income': sum_income,
            'remaining_savings': remaining_savings,
            'amount_over_budget': abs(amount_over_budget),
        }

        return render(request, 'expenses/stats.html', context)
    return redirect('home')


def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        expenses = AddMoneyInfo.objects.filter(user=user).order_by('-Date')
        context = {'expenses': expenses}
        return render(request, 'expenses/tables.html', context)
    return redirect('home')
