"""Create the default lead statuses (idempotent).

Канонические статусы и цвета карточек интерфейса менеджера:

* visitor -> бледно-жёлтый
* order   -> зелёный
* work    -> синий
* lead    -> красный
"""
from django.core.management.base import BaseCommand

from core.models import LeadStatus


class Command(BaseCommand):
    help = "Create default lead statuses used by the bot and manager UI."

    def handle(self, *args, **options):
        for status in LeadStatus.ensure_canonical():
            self.stdout.write(f"ok: {status.name} ({status.color})")
