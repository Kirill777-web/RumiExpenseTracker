from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from .models import UserProfile


def main_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'accounts/main_page.html')


def home(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'accounts/login.html')


def handleSignup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            user.userprofile.profession = form.cleaned_data['profession']
            user.userprofile.savings = form.cleaned_data['savings']
            user.userprofile.income = form.cleaned_data['income']
            user.userprofile.save()
            dj_login(request, user)
            messages.success(
                request, "Your account has been successfully created")
            return redirect('index')
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
            return redirect('index')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('login')
    else:
        # Ensure CSRF token is created for GET requests too
        get_token(request)
    return render(request, 'accounts/login.html')


def custom_csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason})


@login_required
def handleLogout(request):
    request.session.flush()
    auth_logout(request)
    return redirect('login')


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user)
    if request.method == 'POST':
        user_profile.profession = request.POST.get('profession')
        user_profile.savings = request.POST.get('savings')
        user_profile.income = request.POST.get('income')

        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('index')
    return render(request, 'accounts/profile.html', {'profile': user_profile})


@login_required
def profile_edit(request, id):
    user = get_object_or_404(User, id=id, user=request.user)
    return render(request, 'accounts/profile_edit.html', {'user': user})


@login_required
def profile_update(request, id):
    user = get_object_or_404(User, id=id, user=request.user)
    if request.method == "POST":
        user.first_name = request.POST["fname"]
        user.last_name = request.POST["lname"]
        user.email = request.POST["email"]
        user.userprofile.savings = request.POST["savings"]
        user.userprofile.income = request.POST["income"]
        user.userprofile.profession = request.POST["profession"]
        user.userprofile.save()
        user.save()
        return redirect('index')
    return redirect('home')
