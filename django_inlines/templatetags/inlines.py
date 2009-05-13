from django import template
from django.conf import settings

register = template.Library()


@register.filter
def stripinlines(value):
    from django_inlines.inlines import registry
    return registry.inline_finder.sub('', value)


class InlinesNode(template.Node):

    def __init__(self, var_name, template_directory=None, asvar=None):
        self.var_name = template.Variable(var_name)
        self.template_directory = template_directory
        self.asvar = asvar

    def render(self, context):
        try:
            from django_inlines.inlines import registry

            if self.template_directory is None:
                rendered = registry.process(self.var_name.resolve(context))
            else:
                rendered = registry.process(self.var_name.resolve(context), template_dir=self.template_directory)
            if self.asvar:
                context[self.asvar] = rendered
                return ''
            else:
                return rendered
        except:
            if getattr(settings, 'INLINE_DEBUG', False): # Should use settings.TEMPLATE_DEBUG?
                raise
            return ''


@register.tag
def process_inlines(parser, token):
    """
    Searches through the provided content and applies inlines where ever they
    are found.

    Syntax::

        {% process_inlines entry.body [in template_dir] [as varname] }

    Examples::

        {% process_inlines entry.body %}

        {% process_inlines entry.body as body %}

        {% process_inlines entry.body in 'inlines/sidebar' %}

        {% process_inlines entry.body in 'inlines/sidebar' as body %}

    """

    args = token.split_contents()

    if not len(args) in (2, 4, 6):
        raise template.TemplateSyntaxError("%r tag requires either 1, 3 or 5 arguments." % args[0])

    var_name = args[1]

    ALLOWED_ARGS = ['as', 'in']
    kwargs = { 'template_directory': None }
    if len(args) > 2:
        tuples = zip(*[args[2:][i::2] for i in range(2)])
        for k,v in tuples:
            if not k in ALLOWED_ARGS:
                raise template.TemplateSyntaxError("%r tag options arguments must be one of %s." % (args[0], ', '.join(ALLOWED_ARGS)))
            if k == 'in':
                kwargs['template_directory'] = v
            if k == 'as':
                kwargs['asvar'] = v

    return InlinesNode(var_name, **kwargs)
