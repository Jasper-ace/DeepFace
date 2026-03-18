from django.core.management.base import BaseCommand
from face_auth_app.models import RecognitionLog
from face_auth_app.views import get_public_ip, get_server_ip


class Command(BaseCommand):
    help = 'Update log IP addresses to show more meaningful IPs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN - No changes will be made')
        
        # Get server IPs
        public_ip = get_public_ip()
        network_ip = get_server_ip()
        
        self.stdout.write(f'Server Public IP: {public_ip or "Not detected"}')
        self.stdout.write(f'Server Network IP: {network_ip}')
        self.stdout.write('')
        
        # Update logs
        logs = RecognitionLog.objects.all()
        updated_count = 0
        
        for log in logs:
            old_ip = log.ip_address
            new_ip = None
            
            # Update localhost entries to public IP
            if old_ip == '127.0.0.1':
                new_ip = public_ip or network_ip
            # Keep local network IPs as they are (they're meaningful)
            elif old_ip and old_ip.startswith('192.168.'):
                new_ip = old_ip  # Keep as is
            elif old_ip and old_ip.startswith('10.'):
                new_ip = old_ip  # Keep as is
            elif old_ip and old_ip.startswith('172.'):
                new_ip = old_ip  # Keep as is
            else:
                new_ip = old_ip  # Keep as is
            
            if new_ip and new_ip != old_ip:
                self.stdout.write(f'Log {log.id}: {old_ip} -> {new_ip}')
                if not dry_run:
                    log.ip_address = new_ip
                    log.save()
                updated_count += 1
            
        if dry_run:
            self.stdout.write(f'Would update {updated_count} log entries')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} log entries')
            )