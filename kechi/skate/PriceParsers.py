import sys, os

import BlockEx

import json


class PriceParserBase(BlockEx.UrlStreamParser):
    def __init__(self, host, matchers):
        super(PriceParserBase, self).__init__('www.anthropologie.com')
        self.setMatchers(matchers)
        self.regularPrice = None
        self.salePrice = None

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

class AnthropologieParser(PriceParserBase):

    def __init__(self):
        super(AnthropologieParser,
              self).__init__('www.anthropologie.com',
                             [AnthropologieSaleBlock(),
                              AnthropologieRegularBlock()])

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

class BloomingdalesBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'(.+)')
        super(BloomingdalesBlock, self).__init__(openingRegexStrings = [r'<script id="pdp_data" type="application/json">'],
                                                 blockMatchex = matchex,
                                                 endingRegexString = r'</script>')

class BloomingdalesParser(PriceParserBase):

    def __init__(self):
        super(BloomingdalesParser,
              self).__init__('www1.bloomingdales.com',[BloomingdalesBlock()])

    def parsePrice(self, jsonString):
        pdpData = None
        try:
            pdpData = json.loads(jsonString)
        except:
            print('unable to parse: %s, %s' % (jsonString, pdpData))
        if pdpData is None:
            return
        product = pdpData['product']
        prices = product.get('unavailablePrice',None)
        if prices is None:
            return
        self.regularPrice = prices['originalPrice']
        self.salePrice = prices['retailPrice']

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

class NordstromBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+window\.digitalData\s+=\s+(.+);')
        super(NordstromBlock, self).__init__(openingRegexStrings = [r'\s+<script>'],
                                                 blockMatchex = matchex,
                                                 endingRegexString = r'\s+</script>')

class NordstromParser(PriceParserBase):

    def __init__(self):
        super(NordstromParser, self).__init__('shop.nordstrom.com',
                                              [NordstromBlock()])

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
        
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

class PranaBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+var\s+optionsPrice\s+=\s+new\s+Product\.OptionsPrice\((.*)\);\s+')
        super(PranaBlock, self).__init__(openingRegexStrings = [r'^<script type="text/javascript">\s*'],
                                         blockMatchex = matchex,
                                         endingRegexString = r'\s*</script>\s*')

class PranaParser(PriceParserBase):

    def __init__(self):
        super(PranaParser, self).__init__('www.prana.com',[PranaBlock()])
        
    def parsePrice(self, jsonString):
        priceData = json.loads(jsonString)
        self.salePrice = priceData['productPrice']
        self.regularPrice = priceData['productOldPrice']
    
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

class ZaraBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+productData\:\s+(.+),')
        super(ZaraBlock, self).__init__(openingRegexStrings = [r'\s+<script type="text/javascript">'],
                                                 blockMatchex = matchex,
                                                 endingRegexString = r'\s+}\);</script>')

class ZaraParser(PriceParserBase):
    # The image is in the json block shortly after the productData (in xmedias)
    def __init__(self):
        super(ZaraParser, self).__init__('www.zara.com',[ZaraBlock()])

    def parsePrice(self, jsonString):
        pdpData = None
        try:
            pdpData = json.loads(jsonString)
        except:
            print('unable to parse: %s' % jsonString)
        if pdpData is None:
            return
        currentPrice = pdpData.get('productCurrentPrice',None)
        oldPrice = pdpData.get('productOldPrice',None)
        #print('current: %s, old: %s' % (currentPrice, oldPrice))
        if oldPrice is None or oldPrice == '0.0':
            self.regularPrice = currentPrice
            self.salePrice = None
        else:
            self.regularPrice = oldPrice
            self.salePrice = currentPrice
            
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parsePrice(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None



parsers = {'Prana':            PranaParser(),
           'Bloomingdales':    BloomingdalesParser(),
           'Anthropologie':    AnthropologieParser(),
           'Nordstrom':        NordstromParser(),
           'Zara':             ZaraParser()
}

def GetParser(storeName):
    return parsers.get(storeName, None)
