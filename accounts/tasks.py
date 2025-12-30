from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

@shared_task
def send_verification_email(user_email, verification_token, user_id):
    verification_link = f"http://localhost:8000{reverse('verify_email', args=[verification_token])}"
    
    subject = 'Verify Your Email - Employee Management System'
    message = f"""
    Welcome to Employee Management System!
    
    Please verify your email by clicking the link below:
    {verification_link}
    
    If you didn't create this account, please ignore this email.
    
    Thanks,
    Employee Management Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    return f"Verification email sent to {user_email}"