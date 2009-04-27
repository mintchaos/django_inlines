import re
from django.template.loader import render_to_string
from django.template import Context, RequestContext
from django.db.models.base import ModelBase
from django.conf import settings

INLINE_SPLITTER = re.compile(r"""
    (?P<name>[a-z_]+)       # Must start with a lowercase + underscores name
    (?::(?P<variant>\w+))?  # Variant is optional, ":variant"
    (?:(?P<args>[^\Z]+))? # args is everything up to the end
    """, re.VERBOSE)

INLINE_KWARG_PARSER = re.compile(r"""
    (?P<kwargs>(?:\s\b[a-z_]+=\w+\s?)+)?\Z # kwargs match everything at the end in groups " name=arg"
    """, re.VERBOSE)


class InlineUnrenderableError(Exception):
    """
    Any errors that are children of this error will be silenced by inlines.process
    unless settings.INLINE_DEBUG is true.
    """
    pass

class InlineInputError(InlineUnrenderableError):
    pass

class InlineValueError(InlineUnrenderableError):
    pass

class InlineAttributeError(InlineUnrenderableError):
    pass

class InlineNotRegisteredError(InlineUnrenderableError):
    pass

class InlineUnparsableError(InlineUnrenderableError):
    pass


def parse_inline(text):
    """
    Takes a string of text from a text inline and returns a 3 tuple of
    (name, value, **kwargs).
    """

    m = INLINE_SPLITTER.match(text)
    if not m:
        raise InlineUnparsableError
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
            kwargs[str(k)] = v
    return (name, value, kwargs)


def inline_for_model(model):
    """
    A shortcut function to produce ModelInlines for django models
    """

    if not isinstance(model, ModelBase):
        raise ValueError("inline_for_model requires it's argument to be a Django Model")
    class_name = "%sInline" % model._meta.module_name.capitalize()
    return type(class_name, (ModelInline,), dict(model=model))


class InlineBase(object):
    """
    A base class for overriding to provide simple inlines.
    The `render` method is the only required override. It should return a string.
    or at least something that can be coerced into a string.
    """

    def __init__(self, value, variant=None, context=None, template_dir="", **kwargs):
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

    If you instantiate your inline class with a context instance, it'll use
    that to set up your base context.

    Any extra arguments assigned to your inline are passed directly though to
    the context.
    """

    def __init__(self, value, variant=None, context=None, template_dir=None, **kwargs):
        self.value = value
        self.variant = variant
        self.context = context
        self.kwargs = kwargs

        self.template_dirs = []
        if template_dir:
            self.template_dirs.append(template_dir.strip('/').replace("'", '').replace('"', ''))
        self.template_dirs.append('inlines')

    def get_context(self):
        """
        This method must be defined in a subclass
        """
        raise NotImplementedError('This method must be defined in a subclass')

    def get_template_name(self):
        templates = []
        name = self.__class__.name
        for dir in self.template_dirs:
            if self.variant:
                templates.append('%s/%s.%s.html' % (dir, name, self.variant))
            templates.append('%s/%s.html' % (dir, name))
        return templates

    def render(self):
        if self.context:
            context = self.context
        else:
            context = Context()
        context.update(self.kwargs)
        context['variant'] = self.variant
        return render_to_string(self.get_template_name(), self.get_context(), context)


class ModelInline(TemplateInline):
    """
    A base class for creating inlines for Django models. The `model` class
    attribute is the only required override. It should be assigned a django
    model class.
    """

    model = None

    def get_context(self):
        model = self.__class__.model
        if not isinstance(model, ModelBase):
            raise InlineAttributeError('ModelInline requires model to be set to a django model class')
        try:
            value = int(self.value)
            object = model.objects.get(pk=value)
        except ValueError:
            raise InlineInputError("'%s' could not be converted to an int" % self.value)
        except model.DoesNotExist:
            raise InlineInputError("'%s' could not be found in %s.%s" % (self.value, model._meta.app_label, model._meta.module_name))
        return { 'object': object }


class Registry(object):

    def __init__(self):
        self._registry = {}
        self.START_TAG = getattr(settings, 'INLINES_START_TAG', '{{')
        self.END_TAG = getattr(settings, 'INLINES_END_TAG', '}}')

    def register(self, name, cls):
        if not hasattr(cls, 'render'):
            raise TypeError("You may only register inlines with a `render` method")
        cls.name = name
        self._registry[name] = cls

    def unregister(self, name):
        if not name in self._registry:
            raise InlineNotRegisteredError("Inline '%s' not registered. Unable to remove." % name)
        del(self._registry[name])

    def process(self, text, context=None, template_dir=None, **kwargs):
        def render(matchobj):
            try:
                text = matchobj.group(1)
                name, value, inline_kwargs = parse_inline(text)
                try:
                    cls = self._registry[name]
                except KeyError:
                    raise InlineNotRegisteredError('"%s" was not found as a registered inline' % name)
                inline = cls(value, context=context, template_dir=template_dir, **inline_kwargs)
                return str(inline.render())
            # Silence any InlineUnrenderableErrors unless INLINE_DEBUG is True
            except InlineUnrenderableError:
                debug = getattr(settings, "INLINE_DEBUG", False)
                if debug:
                    raise
                else:
                    return ""
        inline_finder = re.compile(r'%(start)s\s*(.+?)\s*%(end)s' % {'start':self.START_TAG, 'end':self.END_TAG})
        text = inline_finder.sub(render, text)
        return text


# The default registry.
registry = Registry()
