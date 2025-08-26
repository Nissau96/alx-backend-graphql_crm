from celery import Celery

# Set the default Django settings module for the 'celery' program
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')

app = Celery('crm')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in the crm app
app.autodiscover_tasks(['crm'], force=True)