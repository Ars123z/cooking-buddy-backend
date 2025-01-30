from django.db import models


from django.contrib.auth import get_user_model

from accounts.models import User
from django.utils import timezone

# Create your models here.


class Video(models.Model):

    video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    channel_name = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=200)
    ingredient_list = models.JSONField()
    method = models.JSONField()
    last_fetched = models.DateTimeField(default=timezone.now)
    
    def __str__(self): 
        return self.title


class WatchHistory(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video, related_name='watched_by_user')


class Labels(models.Model):
    name = models.CharField(max_length=255)
    videos = models.ManyToManyField(Video, related_name='labels')
    region = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

