from django import template

from app.localization import translate

register = template.Library()


@register.simple_tag
def tr(key, default=None, **kwargs):
    return translate(key, default=default, **kwargs)
