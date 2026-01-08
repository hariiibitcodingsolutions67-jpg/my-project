from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('users/', views.admin_users_list, name='admin_users_list'),
    path('user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('user/<int:user_id>/update/', views.admin_user_update, name='admin_user_update'),
    path('user/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('pm/create/', views.pm_create, name='pm_create'),
    path('create-employee/', views.admin_create_employee, name='admin_create_employee'),
    path('projects/', views.admin_projects_list, name='admin_projects_list'),
    path('updates/', views.admin_updates_list, name='admin_updates_list'),
    path('stats/', views.admin_stats, name='admin_stats'),
    
    path('project/create/', views.project_create, name='project_create'),
    path('project/<int:pk>/update/', views.project_update, name='project_update'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('project/<int:project_id>/team/', views.project_team_view, name='project_team_view'),
    path('employee/create/', views.employee_create, name='employee_create'),
    path('employee/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('team/', views.pm_team_view, name='pm_team_view'),
    
    path('todo/create/', views.todo_create, name='todo_create'),
    path('todo/<int:pk>/update/', views.todo_update, name='todo_update'),
    path('todo/<int:pk>/delete/', views.todo_delete, name='todo_delete'),
    path('update/create/', views.daily_update_create, name='daily_update_create'),
    path('update/<int:pk>/update/', views.daily_update_update, name='daily_update_update'),
    path('update/<int:pk>/delete/', views.daily_update_delete, name='daily_update_delete'),
    
    path('profile/update/', views.profile_update, name='profile_update'),
]
