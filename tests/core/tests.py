import unittest
from django_inlines.inlines import Registry, InlineBase, parse_inline
from django_inlines.samples import YoutubeInline

class QuineInline(InlineBase):
    """
    A simple inline that returns itself.
    """
    def render(self):
        bits = []
        if self.variant:
            bits.append(':%s' % self.variant)
        else:
            bits.append('')
        if self.value:
            bits.append(self.value)
        for k, v in self.kwargs.items():
            bits.append("%s=%s" % (k,v))
        else:
            return "{{ quine%s }}" % " ".join(bits)

class DoubleInline(InlineBase):
    """
    A simple inline that doubles itself.
    """
    def render(self):
        value = self.value
        multiplier = 2
        if self.kwargs.has_key('multiplier'):
            try:
                multiplier = int(self.kwargs['multiplier'])
            except ValueError:
                pass
        try:
            value = int(self.value)
        except ValueError:
            pass
        return value*multiplier

class ParserTestCase(unittest.TestCase):
    def testParser(self):
        OUT = ('simple', '', {})
        self.assertEqual(parse_inline('simple'), OUT)
        OUT = ('with', 'a value', {})
        self.assertEqual(parse_inline('with a value'), OUT)
        OUT = ('with', 'a value', {'and': 'args'})
        self.assertEqual(parse_inline('with a value and=args'), OUT)
        OUT = ('with', '', {'just': 'args'})
        self.assertEqual(parse_inline('with just=args'), OUT)
        OUT = ('with', 'complex value http://www.youtube.com/watch?v=nsBAj6eopzc&hd=1&feature=hd#top', {})
        self.assertEqual(parse_inline('with complex value http://www.youtube.com/watch?v=nsBAj6eopzc&hd=1&feature=hd#top'), OUT)
        OUT = ('with', 'complex value http://www.youtube.com/watch?v=nsBAj6eopzc&hd=1&feature=hd#top', {'and': 'args'})
        self.assertEqual(parse_inline('with complex value http://www.youtube.com/watch?v=nsBAj6eopzc&hd=1&feature=hd#top and=args'), OUT)
        OUT = ('with', 'a value', {'variant': 'variant', 'and': 'args', 'more': 'arg'})
        self.assertEqual(parse_inline('with:variant a value and=args more=arg'), OUT)
        OUT = ('with', '', {'variant': 'avariant'})
        self.assertEqual(parse_inline('with:avariant'), OUT)
    

class InlineTestCase(unittest.TestCase):
    def setUp(self):
        inlines = Registry()
        inlines.register('quine', QuineInline)
        inlines.register('double', DoubleInline)
        self.inlines = inlines

    def testQuineInline(self):
        IN = """{{ quine should be the same }}"""
        OUT = """{{ quine should be the same }}"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """the {{ quine }}"""
        OUT = """the {{ quine }}"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """the {{ quine with value }}
        {{ quine with=args }}
        {{ quine:with_variant }}
        {{ quine:with everything even=args }}
        """
        OUT = """the {{ quine with value }}
        {{ quine with=args }}
        {{ quine:with_variant }}
        {{ quine:with everything even=args }}
        """
        self.assertEqual(self.inlines.process(IN), OUT)

    def testDoubleInline(self):
        IN = """{{ double makes more  }}"""
        OUT = """makes moremakes more"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """{{ double 2 }} / {{ double 2 multiplier=3 }}"""
        OUT = """4 / 6"""
        self.assertEqual(self.inlines.process(IN), OUT)

    def testMultipleInlines(self):
        IN = """{{ quine }} and {{ nothing }}"""
        OUT = """{{ quine }} and """
        self.assertEqual(self.inlines.process(IN), OUT)

    def testRemovalOfUnassignedInline(self):
        IN = """this {{ should }} be removed"""
        OUT = """this  be removed"""
        self.assertEqual(self.inlines.process(IN), OUT)

class YoutubeTestCase(unittest.TestCase):
    def setUp(self):
        inlines = Registry()
        inlines.register('youtube', YoutubeInline)
        self.inlines = inlines

    def testYoutubeInlines(self):
        IN = """{{ youtube RXJKdh1KZ0w }}"""
        OUT = """<div class="youtube_video">\n<object width="480" height="295">\n  <param name="movie" value="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>\n</object>  \n</div>\n"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """{{ youtube RXJKdh1KZ0w width=200 height=100 }}"""
        OUT = """<div class="youtube_video">\n<object width="200" height="100">\n  <param name="movie" value="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="200" height="100"></embed>\n</object>  \n</div>\n"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """{{ youtube http://www.youtube.com/watch?v=RXJKdh1KZ0w&hd=1&feature=hd }}"""
        OUT = """<div class="youtube_video">\n<object width="480" height="295">\n  <param name="movie" value="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>\n</object>  \n</div>\n"""
        self.assertEqual(self.inlines.process(IN), OUT)

if __name__ == '__main__':
    unittest.main()
