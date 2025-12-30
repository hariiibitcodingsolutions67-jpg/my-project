import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')

app = Celery('employee_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


### 3.4 `employee_management/__init__.py`

from .celery import app as celery_app

__all__ = ('celery_app',)

    