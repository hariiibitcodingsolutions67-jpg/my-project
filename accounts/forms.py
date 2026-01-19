from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User, Project, Todo, DailyUpdate


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UserCreationForm(BaseUserCreationForm):
    """Form for creating PM and Employee"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control','accept': 'image/*'}),
        help_text='Upload profile picture (optional)'
    )
    
    # ✅ Email Verified Checkbox
    is_verified = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Email Already Verified',
        help_text='Check this if the user has already verified their email (no verification email will be sent)'
    )
    
    # ✅ Active Status Checkbox
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active Account',
        help_text='Uncheck to deactivate this user account'
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_image', 'is_verified', 'is_active', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class ProfileForm(forms.ModelForm):
    """Profile Form for editing user details"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'First Name'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Last Name'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email'})
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control','accept': 'image/*'}),
        help_text='Upload profile picture'
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Account Active'
    )
    
    is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Email Verified'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_image', 'is_active', 'is_verified']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial value for checkboxes if instance exists
        if self.instance and self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active
            self.fields['is_verified'].initial = self.instance.is_verified


# Other forms remain same...
class ProjectForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Project Name'})
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control','placeholder': 'Project Description','rows': 4})
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description']


class TodoForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Todo Title'})
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control','placeholder': 'Description','rows': 3})
    )
    
    status = forms.ChoiceField(
        choices=[('PENDING', 'Pending'),('IN_PROGRESS', 'In Progress'),('COMPLETED', 'Completed')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control','type': 'date'})
    )
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'status', 'date']



class DailyUpdateForm(forms.ModelForm):
    update_text = forms.CharField(  # ✅ Match model field name
        widget=forms.Textarea(attrs={'class': 'form-control','placeholder': 'What did you work on today?','rows': 4}),
        label='Work Description'
    )
    
    working_hours = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': '8.00','step': '0.25','min': '0'}),
        help_text='Enter hours (e.g., 8.5 for 8 hours 30 minutes)'
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control','type': 'date'})
    )
    
    class Meta:
        model = DailyUpdate
        fields = ['update_text', 'working_hours', 'date']