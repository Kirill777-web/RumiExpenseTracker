from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import AddMoneyInfo
from django.contrib.admin.models import LogEntry
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Delete users and handle related records explicitly'

    def add_arguments(self, parser):
        parser.add_argument('user_ids', nargs='+', type=int,
                            help='User IDs to delete')

    def handle(self, *args, **kwargs):
        user_ids = kwargs['user_ids']

        for user_id in user_ids:
            # Delete related AddMoneyInfo records
            AddMoneyInfo.objects.filter(user_id=user_id).delete()

            # Delete related LogEntry records
            LogEntry.objects.filter(user_id=user_id).delete()

            # Delete related UserProfile records
            UserProfile.objects.filter(user_id=user_id).delete()

            # Finally, delete the user
            User.objects.filter(id=user_id).delete()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully deleted user {user_id} and related records'))
