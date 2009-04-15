What's this then?
=================

Django Inlines is an app to let you use include other objects and special 
bits in your text fields.

It uses a registration style so it's easy to set up inlines for any of your apps
or third party applications.


Example:
********

Register your inlines::

  from django_inlines import inlines
  from django_inlines.samples import YoutubeInline
  
  inlines.registry.register('youtube', YoutubeInline)

In your `entry.body`::

  <p>Check out my new video:</p>
  
  {{ youtube http://www.youtube.com/watch?v=RXJKdh1KZ0w }}

In your template::

  {% load inlines %}
  {% process_inlines entry.body %}

Output::

  <p>Check out my new video:</p>

  <div class="youtube_video">
    <object width="480" height="295">
      <param name="movie" value="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1"></param>
      <param name="allowFullScreen" value="true"></param>
      <param name="allowscriptaccess" value="always"></param>
      <embed src="http://www.youtube.com/v/RXJKdh1KZ0w&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="295"></embed>
    </object>
  </div>


Creating inlines
****************

An inline can be any class that provides a `render` method and has an  
`__init__`  that can take these arguments::  

  __init__(self, value, variant=None, context=None, template_dir="", **kwargs)
  
Django Inlines comes with the base inline classes you can subclass to create
your own inlines.


``inlines.InlineBase``
----------------------

  A base class for overriding to provide simple inlines.
  The `render` method is the only required override. It should return a string.
  or at least something that can be coerced into a string.


``inlines.TemplateInline``
--------------------------

  A base class for overriding to provide templated inlines.
  The `get_context` method is the only required override. It should return 
  dictionary-like object that will be fed to the template as the context.
    
  If you instantiate your inline class with a context instance, it'll use
  that to set up your base context.
  
  Any extra arguments assigned to your inline are passed directly though to
  the context.

See ``samples.YoutubeInline`` for an example of a ``TemplateInline``
subclass.

Template inlines render a template named the same as the name they were 
registered as. The youtube inline uses ``inlines/youtube.html``


``inlines.ModelInline``
-----------------------
    
  A base class for creating inlines for Django models. The `model` class
  attribute is the only required override. It should be assigned a django
  model class.

A sample model inline::

  from myapp.models import Photo
  
  class PhotoInline(inlines.Modelinline):
    model = Photo

  inlines.registry.register('photo', PhotoInline)

And in use::

  {{ photo 1 }}

ModelInlines take an object's `id` as it's only value and pass that object into 
the context as ``object``.

Since model inlines will be used very often there is a ``inline_for_model`` 
shortcut method for this. It can be used to register models as inlines directly::

  from django_inlines.inlines import inline_for_model
  inlines.registry.register('photo', inline_for_model(Photo))


Inline syntax
*************

Django inlines use this syntax ``{{ name[:variant] value [argument=value ...] }}``

``name``

  The name the inline has been registered under. Template inlines use this as
  the base name for their templates.
  
``value``

  Any string. It's the requirement of the inline class to parse this string.

``variant`` `optional`

  Variants can be used by the inline class to alter behavior. By default any
  inline that renders a template uses this to check for an alternate template.
  ``{{ youtube:hd <videourl> }}`` would first check for ``inlines/youtube.hd.html``
  before checking for ``inlines/youtube.html``.

``arguments`` `optional`

  Any number of key=value pairs are allowed at the end of an inline. These
  are passed directly to the template as context vars.
  ``{{ youtube:hd <videourl> width=400 height=200 }}``


The template tag
****************

Searches through the provided content and applies inlines where ever they are
found. The current context of your template is passed into to your inline templates.

Syntax::

{% process_inlines entry.body [in template_dir] [as varname] }


Example::

  {% process_inlines entry.body %}

  {% process_inlines entry.body as body %}

  {% process_inlines entry.body in 'inlines/sidebar' %}

  {% process_inlines entry.body in 'inlines/sidebar' as body %}

If given the optional template_dir argument inlines will first check in that 
directory for their template before falling back to ``inlines/<inline_name>.html``

If given [as varname] the tag won't return anything but will instead populate
varname in your context. Then you can apply filters or test against the output.


To do:
******

**Warning:** Django inlines is still under development. Every thing here is 
well tested and functional, but stability isn't promised yet. Important bits 
don't exist yet. These include:

* Better documentation.
* Admin style auto discovery of inlines.py in your apps.
* Adding validation hooks to the base classes.
* A model field and a widget for validation and improved adding in the admin.