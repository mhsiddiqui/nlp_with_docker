from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from urdu_tts.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urdu_tts.settings')

app = Celery('urdu_tts',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
             include=['tts.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()