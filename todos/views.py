# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Todo, DailyUpdate
# from .forms import TodoForm, DailyUpdateForm

# @login_required
# def todo_list(request):
#     if request.user.role != 'EMPLOYEE':
#         messages.error(request, 'Only employees can manage todos.')
#         return redirect('dashboard')
    
#     todos = request.user.todos.all()
#     return render(request, 'todos/todo_list.html', {'todos': todos})

# @login_required
# def todo_create(request):
#     if request.user.role != 'EMPLOYEE':
#         messages.error(request, 'Only employees can create todos.')
#         return redirect('dashboard')
#     #
#     if request.method == 'POST':
#         form = TodoForm(request.POST)
#         if form.is_valid():
#             todo = form.save(commit=False)
#             todo.employee = request.user
#             todo.save()
#             messages.success(request, 'Todo created successfully.')
#             return redirect('todo_list')
#     else:
#         form = TodoForm()
    
#     return render(request, 'todos/todo_form.html', {'form': form, 'title': 'Create Todo'})

# @login_required
# def todo_update(request, todo_id):
#     todo = get_object_or_404(Todo, id=todo_id, employee=request.user)
    
#     if request.method == 'POST':
#         form = TodoForm(request.POST, instance=todo)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Todo updated successfully.')
#             return redirect('todo_list')
#     else:
#         form = TodoForm(instance=todo)
    
#     return render(request, 'todos/todo_form.html', {'form': form, 'title': 'Update Todo'})

# @login_required
# def todo_delete(request, todo_id):
#     todo = get_object_or_404(Todo, id=todo_id, employee=request.user)
    
#     if request.method == 'POST':
#         todo.delete()
#         messages.success(request, 'Todo deleted successfully.')
#         return redirect('todo_list')
    
#     return render(request, 'todos/todo_delete.html', {'todo': todo})

# @login_required
# def daily_update_list(request):
#     if request.user.role != 'EMPLOYEE':
#         messages.error(request, 'Only employees can manage daily updates.')
#         return redirect('dashboard')
    
#     updates = request.user.daily_updates.all()
#     total_hours = getattr(request.user.hours_summary, 'total_hours', 0) if hasattr(request.user, 'hours_summary') else 0
    
#     return render(request, 'todos/daily_update_list.html', {
#         'updates': updates,
#         'total_hours': total_hours
#     })

# @login_required
# def daily_update_create(request):
#     if request.user.role != 'EMPLOYEE':
#         messages.error(request, 'Only employees can create daily updates.')
#         return redirect('dashboard')
    
#     if request.method == 'POST':
#         form = DailyUpdateForm(request.POST)
#         if form.is_valid():
#             update = form.save(commit=False)
#             update.employee = request.user
#             update.save()
#             messages.success(request, 'Daily update created successfully.')
#             return redirect('daily_update_list')
#     else:
#         form = DailyUpdateForm()
    
#     return render(request, 'todos/daily_update_form.html', {'form': form, 'title': 'Create Daily Update'})

# @login_required
# def daily_update_update(request, update_id):
#     update = get_object_or_404(DailyUpdate, id=update_id, employee=request.user)
    
#     if request.method == 'POST':
#         form = DailyUpdateForm(request.POST, instance=update)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Daily update updated successfully.')
#             return redirect('daily_update_list')
#     else:
#         form = DailyUpdateForm(instance=update)
    
#     return render(request, 'todos/daily_update_form.html', {'form': form, 'title': 'Update Daily Update'})

# @login_required
# def daily_update_delete(request, update_id):
#     update = get_object_or_404(DailyUpdate, id=update_id, employee=request.user)
    
#     if request.method == 'POST':
#         update.delete()
#         messages.success(request, 'Daily update deleted successfully.')
#         return redirect('daily_update_list')
    
#     return render(request, 'todos/daily_update_delete.html', {'update': update})

