
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

import BlockEx

import json

from skate.models import Store, Item

class PranaBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+var\s+optionsPrice\s+=\s+new\s+Product\.OptionsPrice\((.*)\);\s+')
        super(PranaBlock, self).__init__(openingRegexStrings = [r'^<script type="text/javascript">\s*'],
                                         blockMatchex = matchex,
                                         endingRegexString = r'\s*</script>\s*')

class PranaParser(BlockEx.UrlStreamParser):

    def __init__(self):
        super(PranaParser, self).__init__('www.prana.com')
        self.setMatchers([PranaBlock()])
        self.regularPrice = None
        self.salePrice = None

    def parsePrice(self, jsonString):
        priceData = json.loads(jsonString)
        self.salePrice = priceData['productPrice']
        self.regularPrice = priceData['productOldPrice']
        print('sale price: %s, regular price: %s' % (self.salePrice,
                                                     self.regularPrice))
    
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

class BloomingdalesBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'(.+)')
        super(BloomingdalesBlock, self).__init__(openingRegexStrings = [r'<script id="pdp_data" type="application/json">'],
                                                 blockMatchex = matchex,
                                                 endingRegexString = r'</script>')

class BloomingdalesParser(BlockEx.UrlStreamParser):

    def __init__(self):
        super(BloomingdalesParser, self).__init__('www1.bloomingdales.com')
        self.setMatchers([BloomingdalesBlock()])
        self.regularPrice = None
        self.salePrice = None

    def parsePrice(self, jsonString):
        pdpData = None
        try:
            pdpData = json.loads(jsonString)
        except:
            print('unable to parse: %s' % jsonString)
        if pdpData is None:
            return
        product = pdpData['product']
        prices = product.get('unavailablePrice',None)
        if prices is None:
            return
        self.regularPrice = prices['originalPrice']
        self.salePrice = prices['retailPrice']
        print('sale price: %s, regular price: %s' % (self.salePrice,
                                                     self.regularPrice))
    
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

class AnthropologieSaleBlock(BlockEx.BlockBase):
    def __init__(self):
        regex = r'\s*<span itemprop="price">(\d+\.?\d+) was\((\d+\.?\d+)\)</span>'

        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(AnthropologieSaleBlock, self).__init__(openingRegexStrings = [],
                                                     blockMatchex = matchex,
                                                     endingRegexString = None)

class AnthropologieRegularBlock(BlockEx.BlockBase):
    def __init__(self):
        regex = r'\s*<span itemprop="price">(\d+\.?\d+)</span>'

        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(AnthropologieRegularBlock, self).__init__(openingRegexStrings = [],
                                                        blockMatchex = matchex,
                                                        endingRegexString = None)

class AnthropologieParser(BlockEx.UrlStreamParser):

    def __init__(self):
        super(AnthropologieParser, self).__init__('www.anthropologie.com')
        self.setMatchers([AnthropologieSaleBlock(), AnthropologieRegularBlock()])
        self.regularPrice = None
        self.salePrice = None

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups is None:
            return
        if len(patternMatchex.groups) == 1:
            self.regularPrice = patternMatchex.groups[0]
            self.salePrice = None
        elif len(patternMatchex.groups) == 2:
            self.regularPrice = patternMatchex.groups[1] 
            self.salePrice = patternMatchex.groups[0]
        # now that we handled it, reset it
        matcher.blockMatchex.groups = None

class NordstromBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+window\.digitalData\s+=\s+(.+);')
        super(NordstromBlock, self).__init__(openingRegexStrings = [r'\s+<script>'],
                                                 blockMatchex = matchex,
                                                 endingRegexString = r'\s+</script>')

class NordstromParser(BlockEx.UrlStreamParser):

    def __init__(self):
        super(NordstromParser, self).__init__('shop.nordstrom.com')
        self.setMatchers([NordstromBlock()])
        self.regularPrice = None
        self.salePrice = None

    def parsePrice(self, jsonString):
        pdpData = None
        try:
            pdpData = json.loads(jsonString)
        except:
            print('unable to parse: %s' % jsonString)
        if pdpData is None:
            return
        product = pdpData['product']
        info = product.get('productInfo',None)
        if info is None:
            return
        self.regularPrice = info['basePrice']
        self.salePrice = info.get('salePrice',None)
        print('regular: %s, sale: %s' % (self.regularPrice, self.salePrice))
        
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

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

    def __init__(self):
        super(Command,self).__init__(self)
        self.parsers = {'Prana': PranaParser(),
                        'Bloomingdales': BloomingdalesParser(),
                        'Anthropologie':AnthropologieParser(),
                        'Nordstrom':NordstromParser()}

    def handle(self, *args, **options):
        stores = Store.objects.all()
        for store in stores:
            parser = self.parsers.get(store.name, None)
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
