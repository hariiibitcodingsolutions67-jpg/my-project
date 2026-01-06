from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone
import uuid
from .models import DailyUpdate, WorkingHoursSummary, User
from .tasks import send_verification_email


@receiver(post_save, sender=DailyUpdate)
@receiver(post_delete, sender=DailyUpdate)
def update_working_hours_summary(sender, instance, **kwargs):
    """Update PM's working hours summary"""
    try:
        employee = instance.employee
        
        if not employee.created_by:
            print(f"⚠️  No PM assigned for {employee.email}")
            return
        
        pm = employee.created_by
        total_hours_data = DailyUpdate.objects.filter(
            employee=employee
        ).aggregate(total=Sum('working_hours'))
        
        total_hours = total_hours_data['total'] or 0
        summary, created = WorkingHoursSummary.objects.get_or_create(
            pm=pm,
            employee=employee
        )
        
        summary.total_hours = total_hours
        summary.last_updated = timezone.now()
        summary.save()
        
        print(f"✅ Updated hours for {employee.email}: {total_hours}h (PM: {pm.email})")
        
    except Exception as e:
        print(f"❌ Signal Error: {str(e)}")


@receiver(post_save, sender=User)
def send_verification_email_signal(sender, instance, created, **kwargs):
    """Send verification email (only if not pre-verified)"""
    
    if created and not instance.is_superuser and not instance.is_verified:
        try:
            if not instance.verification_token:
                token = uuid.uuid4().hex
                User.objects.filter(pk=instance.pk).update(verification_token=token)
                
                # ✅ Match your task parameters
                send_verification_email.delay(
                    user_email=instance.email,
                    verification_token=token,
                    user_id=instance.id
                )
                
                print(f"📧 Verification email queued for {instance.email}")
                
        except Exception as e:
            print(f"❌ Email Signal Error: {str(e)}")
    
    elif created and instance.is_verified:
        print(f"✅ User {instance.email} created with pre-verified status (no email sent)")











# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.db.models import Sum
# from django.utils import timezone
# from .models import DailyUpdate, WorkingHoursSummary, User


# @receiver(post_save, sender=DailyUpdate)
# @receiver(post_delete, sender=DailyUpdate)
# def update_working_hours_summary(sender, instance, **kwargs):
#     """
#     ✨ Jab bhi employee daily update create/update/delete kare,
#        PM ke dashboard mein automatically hours update ho jayein
#     """
#     try:
#         employee = instance.employee
        
#         # Check if employee has a PM
#         if not employee.created_by:
#             print(f"No PM assigned for {employee.email}")
#             return
        
#         pm = employee.created_by
        
#         # Calculate total hours for this employee
#         total_hours_data = DailyUpdate.objects.filter(
#             employee=employee
#         ).aggregate(total=Sum('working_hours'))
        
#         total_hours = total_hours_data['total'] or 0
        
#         # Get or create summary
#         summary, created = WorkingHoursSummary.objects.get_or_create(
#             pm=pm,
#             employee=employee
#         )
        
#         # Update total hours
#         summary.total_hours = total_hours
#         summary.last_updated = timezone.now()
#         summary.save()
        
#         print(f"Updated hours for {employee.email}: {total_hours}h (PM: {pm.email})")
        
#     except Exception as e:
#         print(f"Signal Error: {str(e)}")