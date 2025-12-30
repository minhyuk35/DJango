from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "placeholder"

    def handle(self, *args, **options):
        self.stdout.write("ok")
