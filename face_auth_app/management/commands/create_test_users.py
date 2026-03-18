from django.core.management.base import BaseCommand
from face_auth_app.models import FaceUser
import random
import string
import json
import numpy as np


class Command(BaseCommand):
    help = 'Create test users for testing scalability'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of test users to create')
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing test users first',
        )

    def handle(self, *args, **options):
        count = options['count']
        delete_existing = options['delete_existing']
        
        if delete_existing:
            # Delete existing test users
            deleted_count = FaceUser.objects.filter(username__startswith='testuser').count()
            FaceUser.objects.filter(username__startswith='testuser').delete()
            self.stdout.write(f'Deleted {deleted_count} existing test users')
        
        self.stdout.write(f'Creating {count} test users...')
        
        # Generate proper fake face encoding (128-dimensional array)
        fake_encoding_array = np.random.uniform(-1, 1, 128)
        fake_encoding = json.dumps(fake_encoding_array.tolist())
        
        users_created = 0
        for i in range(count):
            try:
                username = f'testuser{i+1:06d}'  # testuser000001, testuser000002, etc.
                email = f'testuser{i+1:06d}@example.com'
                
                # Random status
                is_active = random.choice([True, True, True, False])  # 75% active
                is_superadmin = random.choice([True, False, False, False, False])  # 20% superadmin
                
                user = FaceUser.objects.create(
                    username=username,
                    email=email,
                    face_encoding=fake_encoding,
                    is_active=is_active,
                    is_superadmin=is_superadmin
                )
                
                users_created += 1
                
                if users_created % 100 == 0:
                    self.stdout.write(f'Created {users_created} users...')
                    
            except Exception as e:
                self.stdout.write(f'Error creating user {i+1}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {users_created} test users')
        )
        
        # Show statistics
        total_users = FaceUser.objects.count()
        active_users = FaceUser.objects.filter(is_active=True).count()
        superadmins = FaceUser.objects.filter(is_superadmin=True).count()
        
        self.stdout.write('')
        self.stdout.write('Current Statistics:')
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Active Users: {active_users}')
        self.stdout.write(f'  Super Admins: {superadmins}')
        self.stdout.write(f'  Test Users: {FaceUser.objects.filter(username__startswith="testuser").count()}')