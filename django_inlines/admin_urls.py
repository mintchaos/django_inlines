from django.conf.urls.defaults import *


urlpatterns = patterns('django_inlines.views',
    url(r'^inline_config\.js$', 'js_inline_config', name='js_inline_config'),
    url(r'^get_inline_form/$', 'get_inline_form', name='get_inline_form'),
)
