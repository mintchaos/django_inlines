import re
from django.template.loader import render_to_string
from django.template import Context, RequestContext

INLINE_SPLITTER = re.compile(r"""
    (?P<name>[a-z_]+)           # Must start with a lowercase + underscores name
    (?::(?P<variant>\w+))?      # Variant is optional, ":variant"
    (?:\s(?P<args>[^\Z]+))?      # args is everything up to the end
    """, re.VERBOSE)
INLINE_KWARG_PARSER = re.compile(r"""
    (?P<kwargs>(?:\s?\b[a-z_]+=\w+\s?)+)?\Z # kwargs match everything at the end in groups " name=arg"
    """, re.VERBOSE)


def parse_inline(text):
    """
    Takes a string of text from a text inline and returns a 3 tuple of 
    (name, value, **kwargs).
    """
    m = INLINE_SPLITTER.match(text)
    if not m:
        raise ValueError
    args = m.group('args')
    name = m.group('name')
    value = ""
    kwtxt = ""
    kwargs = {}
    if args:
        kwtxt = INLINE_KWARG_PARSER.search(args).group('kwargs')
        value = re.sub("%s\Z" % kwtxt, "", args)
        value = value.strip()
    if m.group('variant'):
        kwargs['variant'] = m.group('variant')
    if kwtxt:
        for kws in kwtxt.split():
            k, v = kws.split('=')
            kwargs[k] = v
    return (name, value, kwargs)


class InlineBase(object):
    """
    A base class for overriding to provide simple inlines.
    The `render` method is the only required override. It should return a string.
    or at least something that can be coerced into a string.
    """
    def __init__(self, value, variant=None, **kwargs):
        self.value = value
        self.variant = variant
        self.kwargs = kwargs
    
    def render(self):
        raise NotImplementedError('This method must be defined in a subclass')

class TemplateInline(object):
    """
    A base class for overriding to provide templated inlines.
    The `get_context` method is the only required override. It should return 
    dictionary-like object that will be fed to the template as the context.
    
    If if you initate your inline class with a context instance or it'll use
    that to set up your base context.
    """
    def __init__(self, value, variant=None, context=None, template_dir="inlines", **kwargs):
        self.value = value
        self.variant = variant
        self.template_dir = template_dir.strip('/')
        self.context = context
        self.kwargs = kwargs

    def get_context(self):
        """
        This method should 
        """
        raise NotImplementedError('This method must be defined in a subclass')
    
    def get_template_name(self):
        templates = []
        name = self.__class__.name
        templates.append('%s/%s.html' % (self.template_dir, name))
        if self.variant:
            templates.append('%s/%s.%s.html' % (self.template_dir, name, self.variant))
        return templates
    
    def render(self):
        if self.context:
            context = self.context
        else:
            context = Context()
        context.update(self.kwargs)
        context['variant'] = self.variant
        return render_to_string(self.get_template_name(), self.get_context(), context)

class Registry(object):
    def __init__(self):
        self._registry = {}
        self.START_TAG = "{{"
        self.END_TAG = "}}"
    
    def register(self, name, cls):
        if not hasattr(cls, 'render'):
            raise TypeError("You may only register inlines with a `render` method")
        cls.name = name
        self._registry[name] = cls

    def process(self, text):
        def render(matchobj):
            text = matchobj.group(1)
            try:
                name, value, kwargs = parse_inline(text)
            except ValueError:
                return ""
            try:
                cls = self._registry[name]
                inline = cls(value, **kwargs)
                return str(inline.render())
            except KeyError:
                return ""
        inline_finder = re.compile(r'%(start)s (.+?) %(end)s' % {'start':self.START_TAG, 'end':self.END_TAG})
        text = inline_finder.sub(render, text)
        return text