from django import template

register = template.Library()


@register.simple_tag
def unread_of(counts, key):
    """Look up an int key in a dict passed to the template."""
    try:
        return counts.get(key, 0) if counts else 0
    except AttributeError:
        return 0
