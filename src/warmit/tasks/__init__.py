"""Celery tasks for background processing."""

from celery import Celery
from warmit.config import settings


# Create Celery app
celery_app = Celery(
    "warmit",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["warmit.tasks.warming", "warmit.tasks.response"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Process campaigns every 2 hours during business hours (8am - 8pm)
        "process-campaigns": {
            "task": "warmit.tasks.warming.process_campaigns",
            "schedule": 7200.0,  # Every 2 hours
        },
        # Check for responses every 30 minutes
        "process-responses": {
            "task": "warmit.tasks.response.process_responses",
            "schedule": 1800.0,  # Every 30 minutes
        },
        # Reset daily counters at midnight
        "reset-daily-counters": {
            "task": "warmit.tasks.warming.reset_daily_counters",
            "schedule": {
                "hour": 0,
                "minute": 0,
            },
        },
        # Update metrics daily at 11:59 PM
        "update-metrics": {
            "task": "warmit.tasks.warming.update_metrics",
            "schedule": {
                "hour": 23,
                "minute": 59,
            },
        },
    },
)
