from django import template

from app.localization import normalize_language, translate

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, key, default=None, **kwargs):
    request = context.get("request")
    language = context.get("app_language")
    if not language and request is not None:
        language = normalize_language(getattr(request, "LANGUAGE_CODE", None))
    return translate(key, language=language, default=default, **kwargs)
