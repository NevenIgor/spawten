"""Create the default lead statuses (idempotent)."""
from django.core.management.base import BaseCommand

from core.models import Status

DEFAULT_STATUSES = ["visitor", "contacted", "in progress", "client", "archived"]


class Command(BaseCommand):
    help = "Create default statuses used by the bot and admin."

    def handle(self, *args, **options):
        for name in DEFAULT_STATUSES:
            obj, created = Status.objects.get_or_create(name=name)
            self.stdout.write(f"{'created' if created else 'exists'}: {name}")
