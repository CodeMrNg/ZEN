from django.conf import settings
from django.utils import translation

from .localization import normalize_language
from .services import get_or_create_preferences_for_user


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_name = settings.LANGUAGE_COOKIE_NAME
        should_sync_cookie = False
        preferred_language = None

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            preferences = get_or_create_preferences_for_user(user.pk)
            preferred_language = normalize_language(preferences.ui_language)
            if request.COOKIES.get(cookie_name) != preferred_language:
                request.COOKIES[cookie_name] = preferred_language
                should_sync_cookie = True
            request.LANGUAGE_CODE = preferred_language
            translation.activate(preferred_language)

        response = self.get_response(request)

        if should_sync_cookie and preferred_language and cookie_name not in response.cookies:
            response.set_cookie(
                cookie_name,
                preferred_language,
                max_age=getattr(settings, 'LANGUAGE_COOKIE_AGE', 31536000),
                samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax'),
                secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
            )

        return response
