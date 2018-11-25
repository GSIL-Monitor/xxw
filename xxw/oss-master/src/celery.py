import logging
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
# from raven import Client
# from raven.contrib.celery import register_logger_signal, register_signal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

app = Celery('src')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

#
# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))


# client = Client('http://490753754daa450ba63643ae8833b7f6:786c18fb393e4d989bad11024a0f2c73@127.0.0.1:9000/2')
# register_logger_signal(client)
# register_signal(client)
