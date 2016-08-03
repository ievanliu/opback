from .. import celery
from celery.schedules import crontab
# from datetime import timedelta

celery.conf.update(
    CELERYBEAT_SCHEDULE={
        # Execute daily at Midnight (00:00 A.M)
        'host-synchronization-daily': {
            'task': 'host_sync',
            # 'schedule': timedelta(seconds=5),
            'schedule': crontab(minute='*/2'),
            # 'schedule': crontab(hour=0, minute=0),
        },
    }
)
