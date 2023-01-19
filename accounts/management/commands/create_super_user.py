
from accounts.models import AccountManager, Account
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Account.objects.filter(username='admin').exists():
            AccountManager.objects.create_superuser(
                username='admin',
                password='complexpassword123'
            )
        print('Superuser has been created.')