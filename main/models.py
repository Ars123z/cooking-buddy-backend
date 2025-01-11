from django.db import models

from django.contrib.auth import get_user_model

from accounts.models import User

# Create your models here.


class Video(models.Model):

    video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    channel_name = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=200)
    ingredient_list = models.JSONField()
    method = models.JSONField()


class PlayList(models.Model):

    name = models.CharField(max_length=255)
    videos = models.ManyToManyField(Video, related_name="playlists")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

class WatchHistory(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video, related_name='watched_by_user')

