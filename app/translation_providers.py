import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)

BUILTIN_PROVIDER = "builtin"
GOOGLE_FREE_PROVIDER = "google_free"
SUPPORTED_PROVIDERS = {BUILTIN_PROVIDER, GOOGLE_FREE_PROVIDER}


def get_translation_provider_name():
    provider = str(getattr(settings, "APP_TRANSLATION_PROVIDER", GOOGLE_FREE_PROVIDER) or GOOGLE_FREE_PROVIDER).strip().lower()
    return provider if provider in SUPPORTED_PROVIDERS else GOOGLE_FREE_PROVIDER


def translate_with_provider(text, *, target_language, source_language):
    provider = get_translation_provider_name()
    if not text or provider == BUILTIN_PROVIDER or target_language == source_language:
        return None

    try:
        return _translate_cached(provider, text, source_language, target_language)
    except Exception as exc:  # deep-translator exposes multiple provider-specific exception types
        logger.warning("Machine translation failed with provider %s: %s", provider, exc)
        return None


@lru_cache(maxsize=4096)
def _translate_cached(provider, text, source_language, target_language):
    if provider == GOOGLE_FREE_PROVIDER:
        return _translate_with_google_free(text, source_language=source_language, target_language=target_language)
    return None


def _translate_with_google_free(text, *, source_language, target_language):
    from deep_translator import GoogleTranslator

    translator = GoogleTranslator(source=source_language, target=target_language)
    translated = translator.translate(text=text)
    return translated or None
