from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import AddMoneyInfo
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Clean orphaned records in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning orphaned records...')
        self.clean_orphaned_profiles()
        self.clean_orphaned_money_info()
        self.stdout.write('Finished cleaning orphaned records.')

    def clean_orphaned_profiles(self):
        for profile in UserProfile.objects.all():
            if not User.objects.filter(id=profile.user_id).exists():
                profile.delete()
                self.stdout.write(
                    f'Deleted orphaned profile with ID: {profile.id}')

    def clean_orphaned_money_info(self):
        for money_info in AddMoneyInfo.objects.all():
            if not User.objects.filter(id=money_info.user_id).exists():
                money_info.delete()
                self.stdout.write(
                    f'Deleted orphaned money info with ID: {money_info.id}')
