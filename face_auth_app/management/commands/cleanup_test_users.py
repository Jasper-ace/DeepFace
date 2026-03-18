from django.core.management.base import BaseCommand
from face_auth_app.models import FaceUser


class Command(BaseCommand):
    help = 'Clean up test users with corrupted face encodings'

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up test users...")
        
        # Delete all test users (they have corrupted face encodings)
        test_users = FaceUser.objects.filter(username__startswith='testuser')
        count = test_users.count()
        
        if count > 0:
            test_users.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} test users with corrupted face encodings')
            )
        else:
            self.stdout.write("No test users found to delete")
        
        # Show remaining users
        remaining_users = FaceUser.objects.all()
        self.stdout.write(f"\nRemaining users: {remaining_users.count()}")
        
        for user in remaining_users:
            self.stdout.write(f"  - {user.username} ({user.email})")
        
        self.stdout.write(
            self.style.SUCCESS("\nCleanup complete! Test users removed.")
        )