
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

import BlockEx

import json

from skate.models import Store, Item
from skate import PriceParsers
            
def _sendEmail(recipient, description, originalPrice, salePrice, host, path):
    print('sending mail to %s' % recipient)
    fromAddr = 'mailer@futomen.net'
    subject = 'You have an item on sale'
    url = 'http://%s/%s' % (host, path)
    message = '%s is on sale for %s, down from %s.\n%s' % (description,
                                                           salePrice,
                                                           originalPrice,
                                                           url)
    send_mail(subject, message, fromAddr, [recipient], fail_silently=False)

class Command(BaseCommand):
    can_import_settings = True
    help = 'Finds the urls in the items that are on sale'

#    def __init__(self):
#        super(Command,self).__init__(self)

    def handle(self, *args, **options):
        stores = Store.objects.all()
        for store in stores:
            parser = PriceParsers.GetParser(store.name)
            if parser is None:
                print('no parser for %s' % store.name)
                continue

            print('parsing %s' % store.name) 
            items = Item.objects.filter(store=store)
            for item in items:
                print('item.path: %s' % item.urlPath)
                parser.setPath(item.urlPath)
                parser.parse()
                if parser.salePrice and (parser.salePrice != parser.regularPrice):
                    _sendEmail(item.creator.email, item.identifier,
                               parser.regularPrice, parser.salePrice,
                               store.host, item.urlPath)
                    print('item %s is on sale: %s (old: %s)' % (item.identifier,
                                                                parser.salePrice,
                                                                parser.regularPrice))
