var DjangoInlines = DjangoInlines || {}

DjangoInlines.inlines = [];
{% for inline in inlines %}DjangoInlines.inlines.push('{{ inline.name }}');
{% endfor %}
DjangoInlines.get_inline_form_url = "{% url get_inline_form %}";

{% comment %}
{% for inline in inlines %}
obj = {};
obj.name = "{{ inline.name|escapejs }}";
obj.help = "{{ inline.help|escapejs }}";
obj.variants = {{ inline.variants }};
obj.args = []; {% for arg in inline.args %}obj.args.push({{ arg|safe }});{% endfor %}
{% if inline.app_path %}obj.app_path = "{{ inline.app_path }}";{% else %}obj.app_path = false;{% endif %}
DjangoInlines.registered.push(obj);
{% endfor %}
{% endcomment %}
