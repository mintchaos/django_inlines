from django.db import models
from django.contrib.admin.widgets import AdminTextareaWidget


class DelayedUrlReverse(object):
    def __init__(self, reverse_arg):
        self.reverse_arg = reverse_arg

    def __str__(self):
        from django.core.urlresolvers import reverse, NoReverseMatch
        try:
            url = reverse(self.reverse_arg)
        except NoReverseMatch:
            url = ''
        return url

    def startswith(self, value):
        return str(self).startswith(value)


class InlineWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vLargeTextField vInlineTextArea'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(InlineWidget, self).__init__(attrs=final_attrs)

    class Media:
        css = { 'all': [ 'django_inlines/inlines.css' ] }

        js = [
                'admin/jquery.js',
                DelayedUrlReverse('js_inline_config'),
                'js/admin/RelatedObjectLookups.js',
                'django_inlines/jquery-fieldselection.js',
                'django_inlines/inlines.js'
            ]


class InlineField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {}
        defaults.update(kwargs)
        defaults = {'widget': InlineWidget}
        return super(InlineField, self).formfield(**defaults)