# smartscripts/celery_app.py

from celery import Celery

celery = Celery("smartscripts")
celery.config_from_object("smartscripts.config")

# Optional: auto-discover tasks from all registered apps
celery.autodiscover_tasks([
    "smartscripts.tasks"
])

