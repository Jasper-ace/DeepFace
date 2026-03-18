from django.core.management.base import BaseCommand, CommandError
from face_auth_app.models import FaceUser


class Command(BaseCommand):
    help = 'Make a user a super admin'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make super admin')
        parser.add_argument(
            '--revoke',
            action='store_true',
            help='Revoke super admin privileges instead of granting them',
        )

    def handle(self, *args, **options):
        username = options['username']
        revoke = options['revoke']
        
        try:
            user = FaceUser.objects.get(username=username)
        except FaceUser.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')
        
        if revoke:
            if not user.is_superadmin:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is not a super admin.')
                )
                return
            
            user.is_superadmin = False
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully revoked super admin privileges from "{username}"')
            )
        else:
            if user.is_superadmin:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is already a super admin.')
                )
                return
            
            user.is_superadmin = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made "{username}" a super admin')
            )
            
        # Show current super admins
        superadmins = FaceUser.objects.filter(is_superadmin=True)
        self.stdout.write('')
        self.stdout.write('Current Super Admins:')
        for admin in superadmins:
            self.stdout.write(f'  - {admin.username} ({admin.email})')