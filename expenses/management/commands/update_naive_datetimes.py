import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from expenses.models import AddMoneyInfo


class Command(BaseCommand):
    help = 'Update naive datetime fields to be timezone-aware'

    def handle(self, *args, **kwargs):
        entries = AddMoneyInfo.objects.all()
        updated_count = 0

        for entry in entries:
            if entry.Date.tzinfo is None:  # Check if the datetime is naive
                aware_datetime = timezone.make_aware(
                    entry.Date, timezone=pytz.UTC)
                entry.Date = aware_datetime
                entry.save()
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully updated {updated_count} entries'))
