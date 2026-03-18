from django.core.management.base import BaseCommand
from face_auth_app.models import FaceUser
from face_auth_app.face_recognition_utils import FaceRecognitionService
import json
import numpy as np


class Command(BaseCommand):
    help = 'Fix corrupted face encoding data in the database'

    def handle(self, *args, **options):
        face_service = FaceRecognitionService()
        
        self.stdout.write("Checking face encodings for all users...")
        
        corrupted_users = []
        fixed_users = []
        
        for user in FaceUser.objects.all():
            try:
                # Try to decode the face encoding
                encoding = face_service.decode_face_data(user.face_encoding)
                
                if encoding is None:
                    corrupted_users.append(user.username)
                    self.stdout.write(
                        self.style.ERROR(f"User {user.username}: Corrupted face encoding")
                    )
                else:
                    # Validate the encoding
                    if encoding.shape == (128,):
                        self.stdout.write(
                            self.style.SUCCESS(f"User {user.username}: Valid face encoding")
                        )
                    else:
                        corrupted_users.append(user.username)
                        self.stdout.write(
                            self.style.ERROR(f"User {user.username}: Invalid encoding shape {encoding.shape}")
                        )
                        
            except Exception as e:
                corrupted_users.append(user.username)
                self.stdout.write(
                    self.style.ERROR(f"User {user.username}: Error - {str(e)}")
                )
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"Total users: {FaceUser.objects.count()}")
        self.stdout.write(f"Corrupted encodings: {len(corrupted_users)}")
        self.stdout.write(f"Valid encodings: {FaceUser.objects.count() - len(corrupted_users)}")
        
        if corrupted_users:
            self.stdout.write("\nCorrupted users:")
            for username in corrupted_users:
                self.stdout.write(f"  - {username}")
            
            self.stdout.write(
                self.style.WARNING(
                    "\nThese users will need to re-register their face data."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\nAll face encodings are valid!")
            )