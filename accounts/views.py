from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .models import User, Project, Todo, DailyUpdate, WorkingHoursSummary
from .forms import (
    LoginForm, UserCreationForm, ProjectForm, 
    TodoForm, DailyUpdateForm, ProfileForm
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                if not user.is_verified:
                    messages.error(request, 'Please verify your email first.')
                    return redirect('login')
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def verify_email(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.is_verified = True
    user.verification_token = ''
    user.save()
    messages.success(request, 'Email verified successfully! You can now login.')
    return redirect('login')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user

    if user.role == 'ADMIN':
        return admin_dashboard(request)
    elif user.role == 'PM':
        return pm_dashboard(request)
    elif user.role == 'EMPLOYEE':
        return employee_dashboard(request)

    messages.error(request, "Your role is not configured. Please contact admin.")
    return redirect('login')


def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ADMIN':
            messages.error(request, 'Access denied. Admin only.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_dashboard(request):
    """Main admin dashboard"""
    context = {
        'total_users': User.objects.count(),
        'total_pms': User.objects.filter(role='PM').count(),
        'total_employees': User.objects.filter(role='EMPLOYEE').count(),
        'total_projects': Project.objects.count(),
        'recent_users': User.objects.all().order_by('-date_joined')[:10],
        'recent_projects': Project.objects.all().order_by('-created_at')[:5],
        'recent_updates': DailyUpdate.objects.all().order_by('-created_at')[:10],
    }
    return render(request, 'admin_dashboard.html', context) 
        

@login_required
@admin_required
def admin_users_list(request):
    """List all users"""
    users = User.objects.all().order_by('-date_joined')
    
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
    }           
    return render(request, 'accounts/admin_users_list.html', context)   


@login_required
@admin_required
def admin_user_detail(request, user_id):
    """View user details"""
    user_obj = get_object_or_404(User, id=user_id)
    
    context = {
        'user_obj': user_obj,
    }
    
    if user_obj.role == 'EMPLOYEE':
        context['todos'] = Todo.objects.filter(employee=user_obj)[:10]
        context['updates'] = DailyUpdate.objects.filter(employee=user_obj)[:10]
        context['total_hours'] = DailyUpdate.objects.filter(employee=user_obj).aggregate(
            total=Sum('working_hours')
        )['total'] or 0
    
    elif user_obj.role == 'PM':
        context['projects'] = Project.objects.filter(created_by=user_obj)
        context['employees'] = User.objects.filter(created_by=user_obj, role='EMPLOYEE')
    
    return render(request, 'accounts/admin_user_detail.html', context)


@login_required
@admin_required
def admin_user_delete(request, user_id):
    """Delete a user"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if user_obj.is_superuser:
        messages.error(request, 'Cannot delete superuser')
        return redirect('admin_users_list')
    
    if request.method == 'POST':
        email = user_obj.email
        user_obj.delete()
        messages.success(request, f'User {email} deleted successfully')
        return redirect('admin_users_list')
    
    return render(request, 'accounts/admin_user_delete.html', {'user_obj': user_obj})

@login_required
@admin_required
def pm_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'PM'
            user.created_by = request.user
            user.save()
            messages.success(request, f'PM {user.email} created successfully')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create PM'})


@login_required
@admin_required
def admin_create_employee(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'EMPLOYEE'
            user.created_by = request.user
            user.save()
            messages.success(
                request,
                f'Employee {user.email} created successfully'
            )
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(
        request,
        'accounts/user_form.html',
        {
            'form': form,
            'title': 'Create Employee'
        }
    )

@login_required
@admin_required
def admin_projects_list(request):
    """List all projects"""
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'admin_projects_list.html', {'projects': projects})

@login_required
@admin_required
def admin_updates_list(request):
    """List all daily updates"""
    updates = DailyUpdate.objects.all().order_by('-date')
    
    employee_id = request.GET.get('employee')
    if employee_id:
        updates = updates.filter(employee_id=employee_id)
    
    context = {
        'updates': updates,
        'employees': User.objects.filter(role='EMPLOYEE'),
    }
    return render(request, 'admin_updates_list.html', context)

@login_required
@admin_required
def admin_stats(request):
    """Show detailed statistics"""
    context = {
        'users_by_role': User.objects.values('role').annotate(count=Count('id')),
        'projects_by_pm': Project.objects.values('created_by__email').annotate(count=Count('id')),
        'total_working_hours': DailyUpdate.objects.aggregate(total=Sum('working_hours'))['total'] or 0,
    }
    return render(request, 'admin_stats.html', context)


@login_required
def pm_dashboard(request):
    """PM specific dashboard"""
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    context = {
        'projects': Project.objects.filter(created_by=request.user).order_by('-created_at'),
        'employees': User.objects.filter(created_by=request.user, role='EMPLOYEE'),
        'hours_summary': WorkingHoursSummary.objects.filter(pm=request.user),
        'total_projects': Project.objects.filter(created_by=request.user).count(),
        'total_employees': User.objects.filter(created_by=request.user, role='EMPLOYEE').count(),
    }
    return render(request, 'pm_dashboard.html', context)

@login_required
def project_create(request):
    if request.user.role != 'PM':
        messages.error(request, 'Only PMs can create projects')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project created successfully')
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})

@login_required
def project_update(request, pk):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully')
            return redirect('dashboard')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'project_form.html', {'form': form, 'project': project})

@login_required
def project_delete(request, pk):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully')
        return redirect('dashboard')
    
    return render(request, 'confirm_delete.html', {'object': project, 'type': 'Project'})

@login_required
def employee_create(request):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'EMPLOYEE'
            user.created_by = request.user
            user.save()
            messages.success(
                request,
                'Employee created successfully'
            )
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(
        request,
        'accounts/user_form.html',   
        {
            'form': form,
            'title': 'Create Employee'
        }
    )
    


@login_required
def employee_update(request, pk):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    employee = get_object_or_404(User, pk=pk, created_by=request.user, role='EMPLOYEE')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=employee)
    
    return render(
    request,
    'accounts/user_form.html',
    {
        'form': form,
        'title': 'Update Employee',
        'user_obj': employee
    }
)

@login_required
def employee_delete(request, pk):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    employee = get_object_or_404(User, pk=pk, created_by=request.user, role='EMPLOYEE')
    
    if request.method == 'POST':
        email = employee.email
        employee.delete()
        messages.success(request, f'Employee {email} deleted successfully')
        return redirect('dashboard')
    
    return render(request, 'confirm_delete.html', {'object': employee, 'type': 'Employee'})

@login_required
def pm_team_view(request):
    if request.user.role != 'PM':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    employees = User.objects.filter(created_by=request.user, role='EMPLOYEE').annotate(
        total_hours=Sum('dailyupdate__working_hours'),
        total_todos=Count('todo'),
        completed_todos=Count('todo', filter=Q(todo__status='COMPLETED'))
    )
    
    return render(request, 'pm_team_view.html', {'employees': employees})


@login_required
def employee_dashboard(request):
    """Employee specific dashboard"""
    if request.user.role != 'EMPLOYEE':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    context = {
        'todos': Todo.objects.filter(employee=request.user).order_by('-date')[:10],
        'updates': DailyUpdate.objects.filter(employee=request.user).order_by('-date')[:10],
        'total_hours': DailyUpdate.objects.filter(employee=request.user).aggregate(
            total=Sum('working_hours')
        )['total'] or 0,
        'pending_todos': Todo.objects.filter(employee=request.user, status='PENDING').count(),
        'completed_todos': Todo.objects.filter(employee=request.user, status='COMPLETED').count(),
    }
    return render(request, 'employee_dashboard.html', context)


@login_required
def todo_create(request):
    if request.user.role != 'EMPLOYEE':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.employee = request.user
            todo.save()
            messages.success(request, 'Todo created successfully')
            return redirect('dashboard')
    else:
        form = TodoForm()
    return render(request, 'todo_form.html', {'form': form})

@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, employee=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Todo updated successfully')
            return redirect('dashboard')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo_form.html', {'form': form, 'todo': todo})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, employee=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted')
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': todo, 'type': 'Todo'})

@login_required
def daily_update_create(request):
    if request.user.role != 'EMPLOYEE':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DailyUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.employee = request.user
            update.save()
            messages.success(request, 'Daily update created successfully')
            return redirect('dashboard')
    else:
        form = DailyUpdateForm()
    return render(request, 'update_form.html', {'form': form})

@login_required
def daily_update_update(request, pk):
    update = get_object_or_404(DailyUpdate, pk=pk, employee=request.user)
    
    if request.method == 'POST':
        form = DailyUpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Daily update updated successfully')
            return redirect('dashboard')
    else:
        form = DailyUpdateForm(instance=update)
    
    return render(request, 'update_form.html', {'form': form, 'update': update})

@login_required
def daily_update_delete(request, pk):
    update = get_object_or_404(DailyUpdate, pk=pk, employee=request.user)
    
    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Daily update deleted successfully')
        return redirect('dashboard')
    
    return render(request, 'confirm_delete.html', {'object': update, 'type': 'Daily Update'})

 
@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile_form.html', {'form': form})