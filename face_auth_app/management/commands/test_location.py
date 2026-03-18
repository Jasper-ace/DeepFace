from django.core.management.base import BaseCommand
from face_auth_app.views import get_public_ip
import requests


class Command(BaseCommand):
    help = 'Test IP geolocation functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing IP Geolocation...')
        
        # Get server's public IP
        public_ip = get_public_ip()
        self.stdout.write(f'Server Public IP: {public_ip or "Not detected"}')
        
        if public_ip and public_ip != '127.0.0.1':
            try:
                # Test geolocation API
                response = requests.get(f'http://ip-api.com/json/{public_ip}', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write('\nLocation Data:')
                    self.stdout.write(f'  Country: {data.get("country", "Unknown")}')
                    self.stdout.write(f'  Region: {data.get("regionName", "Unknown")}')
                    self.stdout.write(f'  City: {data.get("city", "Unknown")}')
                    self.stdout.write(f'  ISP: {data.get("isp", "Unknown")}')
                    self.stdout.write(f'  Timezone: {data.get("timezone", "Unknown")}')
                    if data.get('lat') and data.get('lon'):
                        self.stdout.write(f'  Coordinates: {data.get("lat")}, {data.get("lon")}')
                        self.stdout.write(f'  Google Maps: https://www.google.com/maps?q={data.get("lat")},{data.get("lon")}')
                else:
                    self.stdout.write(f'API Error: HTTP {response.status_code}')
            except Exception as e:
                self.stdout.write(f'Error: {str(e)}')
        else:
            self.stdout.write('Cannot test geolocation with local IP')
            
        self.stdout.write('\nLocation feature test completed!')