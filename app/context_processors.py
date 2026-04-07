import calendar
from decimal import InvalidOperation

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .localization import (
    get_language_direction,
    get_language_locale,
    get_language_menu,
    get_rotated_weekday_short_labels,
    normalize_language,
    normalize_week_start_day,
)
from .models import SocialLink, TradingPreference
from .services import ensure_sqlite_decimal_storage_integrity


def app_i18n(request):
    language = normalize_language(getattr(request, "LANGUAGE_CODE", None))
    week_start_day = calendar.SUNDAY

    if getattr(getattr(request, "user", None), "is_authenticated", False):
        try:
            ensure_sqlite_decimal_storage_integrity(user_id=request.user.pk)
            week_start_day = normalize_week_start_day(
                getattr(request.user.trading_preferences, "default_week_start_day", week_start_day)
            )
        except (TradingPreference.DoesNotExist, OperationalError, ProgrammingError, InvalidOperation):
            week_start_day = calendar.SUNDAY

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
        "app_static_version": settings.APP_STATIC_VERSION,
        "app_languages": get_language_menu(language),
        "app_weekday_short_labels": get_rotated_weekday_short_labels(language, firstweekday=week_start_day),
        "app_week_start_day": week_start_day,
        "app_social_links": social_links,
    }
