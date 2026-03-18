import socket
from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    help = 'Run the Django development server on the network IP address'

    def get_network_ip(self):
        """Get the server's network IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def handle(self, *args, **options):
        if not options.get('addrport'):
            network_ip = self.get_network_ip()
            options['addrport'] = f"{network_ip}:8000"
            self.stdout.write(
                self.style.SUCCESS(f'Starting server on network IP: {network_ip}:8000')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Network access: http://{network_ip}:8000')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Local access: http://localhost:8000')
            )
        
        super().handle(*args, **options)