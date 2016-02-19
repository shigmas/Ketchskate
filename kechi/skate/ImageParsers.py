import BlockEx

import json

class ImageParserBase(BlockEx.UrlStreamParser):
    def __init__(self, host, matchers):
        super(ImageParserBase, self).__init__(host)
        self.setMatchers(matchers)
        self.mainImage = None
        self.altImage = None
    

class AnthropologieImageBlock(BlockEx.BlockBase):
    def __init__(self):
        regex = r'\s+<img alt="[\w\s]+" title="[\w\s]+" src="(.+)"\s+/>'


        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(AnthropologieImageBlock, self).__init__(openingRegexStrings = [],
                                                      blockMatchex = matchex,
                                                      endingRegexString = None)

class AnthropologieImageParser(ImageParserBase):

    def __init__(self):
        super(AnthropologieImageParser, self).__init__('www.anthropologie.com',
                                                       [AnthropologieImageBlock()])

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups is None:
            return
        if len(patternMatchex.groups) == 1:
            self.mainImage = patternMatchex.groups[0]
            # now that we handled it, reset it
        matcher.blockMatchex.groups = None

class BloomingdalesMainImageBlock(BlockEx.BlockBase):
    mainImageKey = 'productImage'

    def __init__(self):
        regex = r'<img id="(%s)" itemprop="image" class="PDPImageDisplayMain" src="(.*)"\s+/>' % self.mainImageKey
        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(BloomingdalesMainImageBlock, self).__init__(openingRegexStrings = [],
                                                          blockMatchex = matchex,
                                                          endingRegexString = None)
        
class BloomingdalesImageParser(ImageParserBase):

    def __init__(self):
        self.mainImageMatcher = BloomingdalesMainImageBlock()
        super(BloomingdalesImageParser, self).__init__('www1.bloomingdales.com',
                                                       [self.mainImageMatcher])

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups is None:
            return
        if len(patternMatchex.groups) == 2:
            if patternMatchex.groups[0] == self.mainImageMatcher.mainImageKey:
                self.mainImage = patternMatchex.groups[1]
        # now that we handled it, reset it
        matcher.blockMatchex.groups = None


class NordstromImageBlock(BlockEx.BlockBase):
    def __init__(self):
        regex = r'<script>React\.render\(React.createElement\(product_desktop, (.+)\), document.getElementById\( \'main\' \)\);</script>'

        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(NordstromImageBlock, self).__init__(openingRegexStrings = [],
                                                  blockMatchex = matchex,
                                                  endingRegexString = None)

class NordstromImageParser(ImageParserBase):

    def __init__(self):
        super(NordstromImageParser, self).__init__('shop.nordstrom.com',
                                                   [NordstromImageBlock()])

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups is None:
            return
        if len(patternMatchex.groups) == 1:
            try:
                reactData = json.loads(patternMatchex.groups[0])
            except:
                print('unable to parse json')
            mediaArray = reactData['initialData']['Model']['StyleModel']['StyleMedia']
            # We certainly have at least one image
            self.mainImage = mediaArray[0]['ImageMediaUri']['Large']
            if len(mediaArray) > 2:
                self.altImage = mediaArray[1]['ImageMediaUri']['Large']
                
        # now that we handled it, reset it
        matcher.blockMatchex.groups = None


class PranaMainImageBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+<img src="(.+)"\s+alt=')
        super(PranaMainImageBlock, self).__init__(openingRegexStrings = [r'<!-- MAIN IMAGE -->'],
                                                  blockMatchex = matchex,
                                                  endingRegexString = r'\s+</noscript>')

class PranaAltImageBlock(BlockEx.BlockBase):
    def __init__(self):
        matchex = BlockEx.PatternMatchex(blockRegex = r'\s+<img src="(.+)"\s+alt=')
        super(PranaAltImageBlock, self).__init__(openingRegexStrings = [r'\s+<noscript>', r'\s+<a href="http://www.prana.com/media/catalog'],
                                              blockMatchex = matchex,
                                              endingRegexString = r'\s+</noscript>')

class PranaImageParser(ImageParserBase):
    def __init__(self):
        super(PranaImageParser, self).__init__('www.prana.com',[PranaMainImageBlock(),PranaAltImageBlock()])
        
    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups is None:
            return
        if len(patternMatchex.groups) == 1: 
            if self.mainImage is None:
                self.mainImage = patternMatchex.groups[0]
            else:
                self.altImage = patternMatchex.groups[0]

        # now that we handled it, reset it
        matcher.blockMatchex.groups = None

class ZaraImageBlock(BlockEx.BlockBase):
    def __init__(self):
        regex = r'\s+xmedias\:\s(.*]}})'
        matchex = BlockEx.PatternMatchex(blockRegex = regex)
        super(ZaraImageBlock, self).__init__(openingRegexStrings = [r'\s+flowplayerKey\:\s',r'\s+relatedProducts\:\s'],
                                             blockMatchex = matchex,
                                             endingRegexString = r'\s+}\);')

class ZaraImageParser(ImageParserBase):
    # The image is in the json block shortly after the productData (in xmedias)
    def __init__(self):
        super(ZaraImageParser, self).__init__('www.zara.com',[ZaraImageBlock()])

    def parseImages(self, jsonString):
        pdpData = None
        try:
            pdpData = json.loads(jsonString)
        except:
            print('unable to parse: %s' % jsonString)
        if pdpData is None:
            return
        # There's one key and a value. The key is some number, but the value is
        # a list of images.
        #print(list(pdpData.values())[0])
        xmedia = list(pdpData.values())[0]['xmedias']
        for image in xmedia:
            if image['kind'] == 'full':
                self.mainImage = 'http:%s' % image['url']
            elif image['kind'] == 'other' and self.altImage is None:
                self.altImage = 'http:%s' % image['url']

    def _handleLine(self, matcher):
        patternMatchex = matcher.blockMatchex
        if patternMatchex.groups:
            self.parseImages(patternMatchex.groups[0])
            # now that we handled it, reset it
            matcher.blockMatchex.groups = None

parsers = {'Prana':            PranaImageParser(),
           'Bloomingdales':    BloomingdalesImageParser(),
           'Anthropologie':    AnthropologieImageParser(),
           'Nordstrom':        NordstromImageParser(),
           'Zara':             ZaraImageParser()
}

def GetParser(storeName):
    return parsers.get(storeName, None)
