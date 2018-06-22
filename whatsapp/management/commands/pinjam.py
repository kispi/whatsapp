import json, os
from whatsapp.models.contact import Contact
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Add initial contact information derived from HaloPinjam Project'

    def __init__(self):
        pass

    def handle(self, *args, **options):
        self.pinjam_contact_seed()

    # Running this function will insert halopinjam contacts into database.(without duplication)
    def pinjam_contact_seed(self):
        with open('./whatsapp/migrations/seeds/pinjam.json') as f:
            data = json.load(f)

        print("Execute HaloPinjam contact migration...")
        for phone in data:
            Contact.objects.filter(
                phone=phone['number']
            ).get_or_create(phone=phone['number'])
        print("HaloPinjam contact migration finished.")
