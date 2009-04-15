from django.test import TestCase
from django.template import Template, Context
from django_inlines import inlines
from django_inlines.samples import YoutubeInline
from test_inlines import QuineInline, DoubleInline


class ProcessInlinesTestCase(TestCase):
    def render(self, template_string, context_dict=None):
        """A shortcut for testing template output."""
        if context_dict is None:
            context_dict = {}
        
        c = Context(context_dict)
        t = Template(template_string)
        return t.render(c)
    
    def setUp(self):
        super(ProcessInlinesTestCase, self).setUp()
        
        # Stow.
        self.old_registry = inlines.registry
        inlines.registry = inlines.Registry()
    
    def tearDown(self):
        inlines.registry = self.old_registry
        super(ProcessInlinesTestCase, self).tearDown()
    
    def test_simple_usage(self):
        inlines.registry.register('youtube', YoutubeInline)
        
        template = "{% load inlines %}<p>{% process_inlines body %}</p>"
        context = {
            'body': "This is my YouTube video: {{ youtube C_ZebDKv1zo }}",
        }
        self.assertEqual(self.render(template, context), '<p>This is my YouTube video: <div class="youtube_video">\n<object width="480" height="295">\n  <param name="movie" value="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>\n</object>  \n</div>\n</p>')

    def test_asvar(self):
        inlines.registry.register('youtube', YoutubeInline)
        
        template = "{% load inlines %}{% process_inlines body as body %}<p>{{ body|safe }}</p>"
        context = {
            'body': "This is my YouTube video: {{ youtube C_ZebDKv1zo }}",
        }
        self.assertEqual(self.render(template, context), u'<p>This is my YouTube video: <div class="youtube_video">\n<object width="480" height="295">\n  <param name="movie" value="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>\n</object>  \n</div>\n</p>')

    def test_asvar_and_template_dir(self):
        """
        The template tag shouldn't care what order the arguments are in.
        """
        inlines.registry.register('youtube', YoutubeInline)
        
        template = "{% load inlines %}{% process_inlines body as body in 'youtube_inlines' %}<p>{{ body|safe }}</p>"
        context = {
            'body': "This is my YouTube video: {{ youtube C_ZebDKv1zo }}",
        }
        self.assertEqual(self.render(template, context), u'<p>This is my YouTube video: <div class="youtube_video">\nC_ZebDKv1zo\n</div>\n</p>')

        template = "{% load inlines %}{% process_inlines body in 'youtube_inlines' as body %}<p>{{ body|safe }}</p>"
        self.assertEqual(self.render(template, context), u'<p>This is my YouTube video: <div class="youtube_video">\nC_ZebDKv1zo\n</div>\n</p>')
    
    def test_usage_with_multiple_inlines(self):
        inlines.registry.register('quine', QuineInline)
        inlines.registry.register('double', DoubleInline)
        
        template = "{% load inlines %}<p>{% process_inlines body %}</p>"
        context = {
            'body': "Some text {{ quine Why hello }} but {{ double your fun }}.",
        }
        self.assertEqual(inlines.registry.process(context['body']), 'Some text {{ quine Why hello }} but your funyour fun.')
        self.assertEqual(self.render(template, context), u'<p>Some text {{ quine Why hello }} but your funyour fun.</p>')
    
    def test_usage_with_template_dirs(self):
        inlines.registry.register('youtube', YoutubeInline)
        
        template = "{% load inlines %}<p>{% process_inlines body in 'youtube_inlines' %}</p>"
        context = {
            'body': "This is my YouTube video: {{ youtube C_ZebDKv1zo }}",
        }
        self.assertEqual(self.render(template, context), u'<p>This is my YouTube video: <div class="youtube_video">\nC_ZebDKv1zo\n</div>\n</p>')

    def test_usage_with_template_dirs_fallback(self):
        """
        A if the a template in the specified dir doesn't exist it should fallback
        to using the default of inlines.
        """
        
        from django.conf import settings
        inlines.registry.register('youtube', YoutubeInline)
        
        template = "{% load inlines %}<p>{% process_inlines body in 'nonexistent_inlines' %}</p>"
        context = {
            'body': "This is my YouTube video: {{ youtube C_ZebDKv1zo }}",
        }
        self.assertEqual(self.render(template, context), u'<p>This is my YouTube video: <div class="youtube_video">\n<object width="480" height="295">\n  <param name="movie" value="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1"></param>\n  <param name="allowFullScreen" value="true"></param>\n  <param name="allowscriptaccess" value="always"></param>\n  <embed src="http://www.youtube.com/v/C_ZebDKv1zo&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>\n</object>  \n</div>\n</p>')
