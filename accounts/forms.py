from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User, Project, Todo, DailyUpdate

class LoginForm(forms.Form):
    """Login form with email and password"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class UserCreationForm(BaseUserCreationForm):
    """Form for creating new users (PM or Employee)"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'profile_image', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


# class ProfileForm(forms.ModelForm):
#     """Form for updating user profile"""
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'profile_image')
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#             'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
#         }

class ProfileForm(forms.ModelForm):
    """Profile Form for editing user details (without role)"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Upload profile picture'
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Account Active'
    )
    
    is_verified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
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

class ProjectForm(forms.ModelForm):
    """Form for creating/updating projects"""
    class Meta:
        model = Project
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project Description'}),
        }


class TodoForm(forms.ModelForm):
    """Form for creating/updating todos"""
    class Meta:
        model = Todo
        fields = ('title', 'description', 'status', 'date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Todo Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optional)'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DailyUpdateForm(forms.ModelForm):
    """Form for creating/updating daily updates with working hours"""
    class Meta:
        model = DailyUpdate
        fields = ('date', 'update_text', 'working_hours')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'update_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'What did you work on today?'
            }),
            'working_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0',
                'max': '24',
                'placeholder': 'e.g., 8.5'
            }),
        }
        labels = {
            'update_text': 'Daily Update',
            'working_hours': 'Working Hours',
        }
        help_texts = {'working_hours': 'Enter hours worked (e.g., 8 or 8.5)',}