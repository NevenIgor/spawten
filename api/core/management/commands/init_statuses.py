"""Create the default lead statuses (idempotent)."""
from django.core.management.base import BaseCommand

from core.models import Status

# name -> is order status
DEFAULT_STATUSES = {
    "visitor": False,
    "order": True,
    "contacted": False,
    "in progress": False,
    "client": True,
    "archived": False,
}


class Command(BaseCommand):
    help = "Create default statuses used by the bot and admin."

    def handle(self, *args, **options):
        for name, is_order in DEFAULT_STATUSES.items():
            obj, created = Status.objects.get_or_create(
                name=name, defaults={"order_status": is_order}
            )
            self.stdout.write(f"{'created' if created else 'exists'}: {name}")
