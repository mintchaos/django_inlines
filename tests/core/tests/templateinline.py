import unittest
from django_inlines.inlines import Registry
from django_inlines.samples import YoutubeInline


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
