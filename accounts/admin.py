from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Project, Todo, DailyUpdate, WorkingHoursSummary


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ('email', 'get_full_name_display', 'role', 'is_verified', 'is_active', 'created_by_display', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_image')}),
        ('Permissions', {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Relationships', {'fields': ('created_by',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_verified', 'created_by'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_full_name_display(self, obj):
        """Display full name or email"""
        return obj.get_full_name() or '-'
    get_full_name_display.short_description = 'Name'
    
    def created_by_display(self, obj):
        """Display who created this user"""
        return obj.created_by.email if obj.created_by else 'System'
    created_by_display.short_description = 'Created By'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Project Admin"""
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'created_by__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Todo Admin"""
    list_display = ('title', 'employee', 'status', 'date', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('title', 'description', 'employee__email')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Todo Information', {
            'fields': ('employee', 'title', 'description', 'status', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter todos based on user role"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'EMPLOYEE':
            return qs.filter(employee=request.user)
        return qs.none()


@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    """Daily Update Admin"""
    list_display = ('employee', 'date', 'working_hours', 'update_preview', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('employee__email', 'update_text')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Update Information', {
            'fields': ('employee', 'date', 'working_hours', 'update_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def update_preview(self, obj):
        """Show preview of update text"""
        return obj.update_text[:50] + '...' if len(obj.update_text) > 50 else obj.update_text
    update_preview.short_description = 'Update Preview'
    
    def get_queryset(self, request):
        """Filter updates based on user role"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'EMPLOYEE':
            return qs.filter(employee=request.user)
        if request.user.role == 'PM':
            return qs.filter(employee__created_by=request.user)
        return qs.none()


@admin.register(WorkingHoursSummary)
class WorkingHoursSummaryAdmin(admin.ModelAdmin):
    """Working Hours Summary Admin"""
    list_display = ('employee', 'pm', 'total_hours_display', 'last_updated')
    list_filter = ('pm', 'last_updated')
    search_fields = ('employee__email', 'pm__email')
    readonly_fields = ('employee', 'pm', 'total_hours', 'last_updated')
    
    def total_hours_display(self, obj):
        """Display total hours with color coding"""
        hours = obj.total_hours
        if hours >= 160:  
            color = 'green'
        elif hours >= 80: 
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} hrs</span>',
            color, hours
        )
    total_hours_display.short_description = 'Total Hours'
    
    def has_add_permission(self, request):
        """Prevent manual creation - auto-generated by signals"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion"""
        return True
    
    def get_queryset(self, request):
        """Filter summaries based on user role"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'PM':
            return qs.filter(pm=request.user)
        return qs.none()