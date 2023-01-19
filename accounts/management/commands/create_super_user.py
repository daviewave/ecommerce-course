
from accounts.models import AccountManager, Account
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Account.objects.filter(username='admin').exists():
            AccountManager.objects.create_superuser(
                email='admin@admin.com'
                username='admin',
                password='admin',
                first_name='admin',
                last_name='admin'
            )
        print('Superuser has been created.')