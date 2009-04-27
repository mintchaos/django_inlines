import unittest
from django.conf import settings
from django_inlines.inlines import Registry, parse_inline, InlineUnparsableError
from core.tests.test_inlines import DoubleInline, QuineInline, KeyErrorInline

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
        OUT = (u'with', u'complex value http://www.youtube.com/watch?v=nsBAj6eopzc', {'and': 'args'})
        self.assertEqual(parse_inline(u'with complex value http://www.youtube.com/watch?v=nsBAj6eopzc and=args'), OUT)
        OUT = ('with', 'a value', {'variant': 'variant', 'and': 'args', 'more': 'arg'})
        self.assertEqual(parse_inline('with:variant a value and=args more=arg'), OUT)
        OUT = ('with', '', {'variant': 'avariant'})
        self.assertEqual(parse_inline('with:avariant'), OUT)

class RegistrySartEndTestCase(unittest.TestCase):

    def setUp(self):
        inlines = Registry()
        inlines.register('double', DoubleInline)
        inlines.START_TAG = '<<'
        inlines.END_TAG = '>>'
        self.inlines = inlines

    def testDifferentSartEnds(self):
        # self.assertEqual(self.inlines.START_TAG, "<<")
        IN = """<< double makes more  >>"""
        OUT = """makes moremakes more"""
        self.assertEqual(self.inlines.process(IN), OUT)
        IN = """<< double 2 >> / << double 2 multiplier=3 >>"""
        OUT = """4 / 6"""
        self.assertEqual(self.inlines.process(IN), OUT)

class InlineTestCase(unittest.TestCase):

    def setUp(self):
        inlines = Registry()
        inlines.register('quine', QuineInline)
        inlines.register('double', DoubleInline)
        self.inlines = inlines

    def tearDown(self):
        settings.INLINE_DEBUG = False

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

    def test_empty_inline(self):
        IN = """this {{ 234 }} be removed"""
        OUT = """this  be removed"""
        self.assertEqual(self.inlines.process(IN), OUT)
        settings.INLINE_DEBUG = True
        self.assertRaises(InlineUnparsableError, self.inlines.process, IN)

    def test_keyerrors(self):
        """
        A regression test to make sure KeyErrors thrown by inlines
        aren't silenced in render anymore.
        """
        self.inlines.register('keyerror', KeyErrorInline)
        IN = "{{ keyerror fail! }}"
        self.assertRaises(KeyError, self.inlines.process, IN)