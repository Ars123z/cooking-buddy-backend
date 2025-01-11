from django.contrib import admin

from main.models import PlayList, Video, WatchHistory

# Register your models here.

admin.site.register(Video)
admin.site.register(PlayList)
admin.site.register(WatchHistory)