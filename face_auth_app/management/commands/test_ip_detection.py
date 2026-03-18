from django.core.management.base import BaseCommand
from django.test import RequestFactory
from face_auth_app.views import get_client_ip, get_server_ip, get_public_ip, is_private_ip


class Command(BaseCommand):
    help = 'Test IP address detection functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing IP Detection...'))
        
        # Test server IP detection
        server_ip = get_server_ip()
        self.stdout.write(f'Server Network IP: {server_ip}')
        
        # Test public IP detection
        public_ip = get_public_ip()
        self.stdout.write(f'Server Public IP: {public_ip or "Could not detect"}')
        
        # Test private IP detection
        test_ips = [
            '127.0.0.1',
            '192.168.1.100',
            '10.0.0.1',
            '172.16.0.1',
            '8.8.8.8',
            '1.1.1.1'
        ]
        
        self.stdout.write('\nTesting private IP detection:')
        for ip in test_ips:
            is_private = is_private_ip(ip)
            self.stdout.write(f'{ip}: {"Private" if is_private else "Public"}')
        
        # Test with mock request
        factory = RequestFactory()
        
        # Test local request
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        detected_ip = get_client_ip(request)
        self.stdout.write(f'\nLocal request IP: {detected_ip}')
        
        # Test forwarded request
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.1'
        detected_ip = get_client_ip(request)
        self.stdout.write(f'Forwarded request IP: {detected_ip}')
        
        self.stdout.write(self.style.SUCCESS('\nIP detection test completed!'))