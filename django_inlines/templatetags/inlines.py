from django import template


register = template.Library()


class InlinesNode(template.Node):
    def __init__(self, var_name, template_directory=None):
        self.var_name = template.Variable(var_name)
        self.template_directory = template_directory
    
    def render(self, context):
        try:
            from django_inlines.inlines import registry
            
            if self.template_directory is None:
                return registry.process(self.var_name.resolve(context))
            else:
                return registry.process(self.var_name.resolve(context), template_dir=self.template_directory)
        except:
            return ''


@register.tag
def process_inlines(parser, token):
    """
    Searches through the provided content and applies inlines whereever they are
    found.
    
    Example::
    
        {% process_inlines body %}
        
        {% process_inlines body in 'youtube_inlines' %}
    
    """
    args = token.split_contents()
    
    if not len(args) in (2, 4):
        raise template.TemplateSyntaxError("%r tag requires either 1 or 3 arguments." % args[0])
    
    var_name = args[1]
    template_directory = None
    
    if len(args) == 4:
        if args[2] != 'in':
            raise template.TemplateSyntaxError("%r tag's second argument should be 'in' if supplying a template directory." % args[0])
        
        template_directory = args[3]
    
    return InlinesNode(var_name, template_directory)
