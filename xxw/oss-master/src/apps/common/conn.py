import redis

from django.conf import settings


redis_conn = redis.StrictRedis(host=settings.REDIS_HOST,
                               port=settings.REDIS_PORT,
                               password=settings.REDIS_PASSWORD)