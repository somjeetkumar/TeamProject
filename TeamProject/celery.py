import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "TeamProject.settings"
)

app = Celery("TeamProject")

app.conf.broker_url = "redis://127.0.0.1:6379/0"
app.conf.result_backend = "redis://127.0.0.1:6379/1"

app.autodiscover_tasks()