from django.db.utils import OperationalError, ProgrammingError

from .localization import (
    get_current_language_code,
    get_language_direction,
    get_language_locale,
    get_language_menu,
    get_weekday_short_labels,
)
from .models import SocialLink


def app_i18n(request):
    language = get_current_language_code()
    try:
        social_links = list(
            SocialLink.objects.filter(is_active=True).order_by('sort_order', 'pk')[:3]
        )
    except (OperationalError, ProgrammingError):
        social_links = []

    return {
        "app_language": language,
        "app_language_locale": get_language_locale(language),
        "app_language_direction": get_language_direction(language),
        "app_languages": get_language_menu(language),
        "app_weekday_short_labels": get_weekday_short_labels(language),
        "app_social_links": social_links,
    }
