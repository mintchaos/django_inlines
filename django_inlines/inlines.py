import re

INLINE_SPLITTER = re.compile(r"""
    (?P<name>[a-z_]+)           # Must start with a lowercase + underscores name
    (?::(?P<varient>\w+))?      # Varient is optional, ":varient"
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
    if m.group('varient'):
        kwargs['varient'] = m.group('varient')
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
    def __init__(self, value, varient=None, **kwargs):
        self.value = value
        self.varient = varient
        self.kwargs = kwargs
    
    def render(self):
        raise NotImplementedError('This method must be defined in a subclass')

class TemplateInline(object):
    """
    A base class for overriding to provide templated inlines.
    The `get_context` method is the only required override. It should return 
    dictionary-like object that will be fed to the template as the context.
    """
    def __init__(self, value, varient=None, request=None, template_dir="inlines", **kwargs):
        self.value = value
        self.varient = varient
        self.template_dir = template_dir.strip('/')
        self.request = request
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
        if self.varient:
            templates.append('%s/%s.%s.html' % (self.template_dir, name, self.varient))
        return templates
    
    def render(self):
        raise NotImplementedError('This method must be defined in a subclass')


class Registry(object):
    
    def __init__(self):
        self._registry = {}
    
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
            
        text = re.sub(r'{{ ([^}]+) }}', render, text)
        return text