from django.core.management.base import BaseCommand
from django.utils import timezone
from face_auth_app.models import RecognitionLog
import pytz


class Command(BaseCommand):
    help = 'Fix log timestamps to correct timezone'

    def handle(self, *args, **options):
        self.stdout.write('Fixing log timestamps...')
        
        # Get timezone
        manila_tz = pytz.timezone('Asia/Manila')
        
        # Update all logs
        logs = RecognitionLog.objects.all()
        updated_count = 0
        
        for log in logs:
            # If the log timestamp is naive (no timezone), assume it was UTC
            if timezone.is_naive(log.detected_at):
                # Convert from UTC to Manila timezone
                utc_time = pytz.utc.localize(log.detected_at)
                manila_time = utc_time.astimezone(manila_tz)
                log.detected_at = manila_time
                log.save()
                updated_count += 1
                
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} log timestamps')
        )