
from django.core.management.base import BaseCommand

import BlockEx

import json

from skate.models import Store, Item
from skate import ImageParsers
            

class Command(BaseCommand):
    can_import_settings = True
    help = 'Updates the images for Items as the references change. For all stores, pass -1'

    def add_arguments(self, parser):
        parser.add_argument('store_id', nargs='+', type=int)
    
    def handle(self, *args, **options):
        storeId = options['store_id'][0]
        # It's required to have the store id, and it can only be one element
        stores = None
        
        if storeId == -1:
            stores = Store.objects.all()
        else:
            stores = Store.objects.filter(pk=storeId)

        for store in stores:
            # Get all the items in the store
            items = Item.objects.filter(store = store)
            # XXX - it's hardcoded in the parser. We should get it from data
            parser = ImageParsers.GetParser(store.name)
            for item in items:
                parser.setPath(item.urlPath)
                parser.parse()
                didChange = False
                if parser.mainImage is not None:
                    print('setting image url to %s' % parser.mainImage)
                    item.mainImageUrl = parser.mainImage
                    didChange = True
                if parser.altImage is not None:
                    print('setting alt url to %s' % parser.altImage)
                    item.altImageUrl = parser.altImage
                    didChange = True
                if didChange:
                    item.save()
