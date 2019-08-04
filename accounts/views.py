from django.contrib import auth
from time_tracker.models import Developer
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from accounts.forms import DeveloperCreationForm, RegistrationForm


def login(request):
    args = dict()
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            args['profile'] = user
            return redirect('/', args)
        else:
            args['login_error'] = 'User not found!'
            return render(request, 'login/login.html', args)
    else:
        return render(request, 'login/login.html', args)


def logout(request):
    auth.logout(request)
    return redirect('homepage')


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def register_step_1(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:register-step-2', user_id=user.pk)
        return render(request, 'register/register_1.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, 'register/register_1.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def register_step_2(request, user_id):
    if request.method == 'POST':
        form = DeveloperCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('accounts:user-list')
        return render(request, 'register/register_2.html', {'form': form})
    else:
        form = DeveloperCreationForm(initial={'user': User.objects.get(id=user_id)})
        return render(request, 'register/register_2.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def user_list(request):
    users = Developer.objects.all()
    return render(request, 'list/index.html', {'users': users})
