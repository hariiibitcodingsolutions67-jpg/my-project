from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone
from .models import DailyUpdate, WorkingHoursSummary, User


@receiver(post_save, sender=DailyUpdate)
@receiver(post_delete, sender=DailyUpdate)
def update_working_hours_summary(sender, instance, **kwargs):
    """
    ✨ Jab bhi employee daily update create/update/delete kare,
       PM ke dashboard mein automatically hours update ho jayein
    """
    try:
        employee = instance.employee
        
        # Check if employee has a PM
        if not employee.created_by:
            print(f"No PM assigned for {employee.email}")
            return
        
        pm = employee.created_by
        
        # Calculate total hours for this employee
        total_hours_data = DailyUpdate.objects.filter(
            employee=employee
        ).aggregate(total=Sum('working_hours'))
        
        total_hours = total_hours_data['total'] or 0
        
        # Get or create summary
        summary, created = WorkingHoursSummary.objects.get_or_create(
            pm=pm,
            employee=employee
        )
        
        # Update total hours
        summary.total_hours = total_hours
        summary.last_updated = timezone.now()
        summary.save()
        
        print(f"Updated hours for {employee.email}: {total_hours}h (PM: {pm.email})")
        
    except Exception as e:
        print(f"Signal Error: {str(e)}")