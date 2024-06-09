from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import UserProfile


def main_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'accounts/main_page.html')


def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/expenses/index/')
    return render(request, 'accounts/login.html')


def handleSignup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            UserProfile.objects.create(
                user=user,
                profession=form.cleaned_data['profession'],
                savings=form.cleaned_data['savings'],
                income=form.cleaned_data['income']
            )
            messages.success(
                request, "Your account has been successfully created")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def handlelogin(request):
    if request.method == 'POST':
        loginuname = request.POST["loginuname"]
        loginpassword1 = request.POST["loginpassword1"]
        user = authenticate(username=loginuname, password=loginpassword1)
        if user is not None:
            dj_login(request, user)
            request.session['is_logged'] = True
            request.session["user_id"] = user.id
            messages.success(request, "Successfully logged in")
            return redirect('/expenses/index/')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('login')
    return render(request, 'accounts/login.html')


def handleLogout(request):
    del request.session['is_logged']
    del request.session["user_id"]
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('home')


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user)
    if request.method == 'POST':
        user_profile.profession = request.POST.get('profession')
        user_profile.savings = request.POST.get('savings')
        user_profile.income = request.POST.get('income')

        # Handle profile picture upload
        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'profile': user_profile})


def profile_edit(request, id):
    if request.session.has_key('is_logged'):
        user = User.objects.get(id=id)
        return render(request, 'accounts/profile_edit.html', {'user': user})
    return redirect('home')


def profile_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST["fname"]
            user.last_name = request.POST["lname"]
            user.email = request.POST["email"]
            user.userprofile.savings = request.POST["savings"]
            user.userprofile.income = request.POST["income"]
            user.userprofile.profession = request.POST["profession"]
            user.userprofile.save()
            user.save()
            return redirect('profile')
    return redirect('home')
