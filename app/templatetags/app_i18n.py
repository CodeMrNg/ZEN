from django import template

from app.formatting import format_decimal_compact, format_decimal_thousands_compact
from app.localization import normalize_language, translate

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, key, default=None, **kwargs):
    request = context.get("request")
    language = context.get("app_language")
    if not language and request is not None:
        language = normalize_language(getattr(request, "LANGUAGE_CODE", None))
    return translate(key, language=language, default=default, **kwargs)


@register.filter
def compact_number(value, decimals=2):
    try:
        decimal_places = int(decimals)
    except (TypeError, ValueError):
        decimal_places = 2
    return format_decimal_compact(value, decimal_places=decimal_places, use_grouping=False)


@register.filter
def compact_number_grouped(value, decimals=2):
    try:
        decimal_places = int(decimals)
    except (TypeError, ValueError):
        decimal_places = 2
    return format_decimal_compact(value, decimal_places=decimal_places, use_grouping=True)


@register.filter
def compact_amount(value, decimals=2):
    try:
        decimal_places = int(decimals)
    except (TypeError, ValueError):
        decimal_places = 2
    return format_decimal_thousands_compact(
        value,
        decimal_places=decimal_places,
        use_grouping_below_threshold=True,
    )
