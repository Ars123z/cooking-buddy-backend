from django.core.management.base import BaseCommand
from main.models import Video
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Deletes all videos older than 20 days"

    def handle(self, *args, **options):
        threshold_date = timezone.now() - timedelta(days=25)
        old_videos = Video.objects.filter(last_fetched__lt=threshold_date)
        count = old_videos.count()

        if count > 0:
            old_videos.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} old videos."))
        else:
            self.stdout.write(self.style.WARNING("No old videos found."))