# task_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import Invitation

def home(request):
    return redirect('task_list')

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        completed = request.POST.get('completed') == 'on'

        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'tasks/task_form.html')

        Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            completed=completed
        )
        messages.success(request, 'Task created successfully.')
        return redirect('task_list')
    else:
        return render(request, 'tasks/task_form.html')

@login_required
def task_edit(request, task_id):
    task = Task.objects.filter(id=task_id, user=request.user).first()
    if not task:
        messages.error(request, 'Task not found.')
        return redirect('task_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        completed = request.POST.get('completed') == 'on'

        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'tasks/task_form.html', {'task': task})

        task.title = title
        task.description = description
        task.completed = completed
        task.save()

        messages.success(request, 'Task updated successfully.')
        return redirect('task_list')
    else:
        return render(request, 'tasks/task_form.html', {'task': task})

@login_required
def task_delete(request, task_id):
    task = Task.objects.filter(id=task_id, user=request.user).first()
    if not task:
        messages.error(request, 'Task not found.')
        return redirect('task_list')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


def register(request, code):
    try:
        invitation = Invitation.objects.get(code=code, accepted=False)
    except Invitation.DoesNotExist:
        messages.error(request, 'Invalid or expired invitation link.')
        return redirect('account_login')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'tasks/register.html', {'code': code})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'tasks/register.html', {'code': code})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'tasks/register.html', {'code': code})

        # Create user
        user = User.objects.create_user(username=username, email=invitation.email, password=password)
        invitation.accepted = True
        invitation.save()

        user = authenticate(username=username, password=password)

        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('task_list')
    else:
        return render(request, 'tasks/register.html', {'code': code})