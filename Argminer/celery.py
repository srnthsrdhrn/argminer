from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task
# set the default Django settings module for the 'celery' program.
from Argminer import settings
from Argminer.settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Argminer.settings')

app = Celery('Argminer', broker=CELERY_BROKER_URL, accept_content=['pickle'],
             task_serializer='pickle')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)


@shared_task
def crawler_task(parent_id=None, starting_user=None, starting_token=None, crawl_friends=False, follower_threshold=0) -> None:
    from twitter.core.crawler import CelebrityCrawler
    from twitter.models import CrawlerTasks
    crawl_task = CrawlerTasks.objects.create(starting_user=starting_user, starting_token=starting_token,
                                             crawl_friends=crawl_friends, parent_id=parent_id)
    crawl_obj = CelebrityCrawler(starting_token=starting_token, starting_user=starting_user, crawl_friends=crawl_friends,
                                 follower_threshold=follower_threshold, crawl_obj_id=crawl_task.id)
    crawl_obj.crawl()
