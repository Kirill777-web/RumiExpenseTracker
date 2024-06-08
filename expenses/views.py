import datetime
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from .models import AddMoneyInfo


def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = AddMoneyInfo.objects.filter(
            user=user).order_by('-Date')
        paginator = Paginator(addmoney_info, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        return render(request, 'expenses/index.html', context)
    return redirect('home')


def addmoney(request):
    return render(request, 'expenses/addmoney.html')


def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            date = request.POST["Date"]
            category = request.POST["Category"]
            add = AddMoneyInfo(user=user1, add_money=add_money,
                               quantity=quantity, Date=date, Category=category)
            add.save()
            return redirect('index')
    return redirect('home')


def addmoney_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            add = AddMoneyInfo.objects.get(id=id)
            add.add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add.save()
            return redirect('index')
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


def charts(request):
    return render(request, 'expenses/charts.html')


def stats(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = AddMoneyInfo.objects.filter(
            user=user1, Date__gte=one_month_ago, Date__lte=todays_date)
        sum = 0
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum = sum + i.quantity
        addmoney_info.sum = sum
        sum1 = 0
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 = sum1 + i.quantity
        addmoney_info.sum1 = sum1
        x = user1.userprofile.Savings + addmoney_info.sum1 - addmoney_info.sum
        y = user1.userprofile.Savings + addmoney_info.sum1 - addmoney_info.sum
        if x < 0:
            messages.warning(request, 'Your expenses exceeded your savings')
            x = 0
        if x > 0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
        return render(request, 'expenses/stats.html', {'addmoney': addmoney_info})
    return redirect('home')


def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        expenses = AddMoneyInfo.objects.filter(user=user).order_by('-Date')
        context = {'expenses': expenses}
        return render(request, 'expenses/tables.html', context)
    return redirect('home')
