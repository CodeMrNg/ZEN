"""
Django settings for journal project.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path, *, override: bool = True) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if override or key not in os.environ:
            os.environ[key] = value


DOTENV_OVERRIDE = str(os.environ.get("DJANGO_DOTENV_OVERRIDE", "true")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

load_env_file(BASE_DIR / ".env", override=DOTENV_OVERRIDE)


def env(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    value = os.environ.get(name, default)
    if required and (value is None or value == ""):
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value


def env_bool(name: str, default: bool = False) -> bool:
    value = str(env(name, str(default))).strip().lower()
    return value in {"1", "true", "yes", "on"}


def env_int(name: str, default: int = 0) -> int:
    value = env(name, str(default))
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(f"Environment variable {name} must be an integer.") from exc


def env_list(name: str, default: str = "") -> list[str]:
    value = env(name, default) or ""
    return [item.strip() for item in value.split(",") if item.strip()]


def env_path(name: str, default: str) -> Path:
    raw_value = Path(env(name, default) or default)
    return raw_value if raw_value.is_absolute() else BASE_DIR / raw_value


def build_database_config() -> dict[str, object]:
    database_url = env("DATABASE_URL")
    conn_max_age = env_int("DB_CONN_MAX_AGE", 60)

    if database_url:
        parsed = urlparse(database_url)
        scheme = parsed.scheme.split("+", 1)[0]
        engine_map = {
            "sqlite": "django.db.backends.sqlite3",
            "sqlite3": "django.db.backends.sqlite3",
            "postgres": "django.db.backends.postgresql",
            "postgresql": "django.db.backends.postgresql",
            "pgsql": "django.db.backends.postgresql",
            "mysql": "django.db.backends.mysql",
        }
        engine = engine_map.get(scheme)
        if not engine:
            raise ImproperlyConfigured(
                "Unsupported DATABASE_URL scheme. Use sqlite, postgresql or mysql."
            )

        if engine == "django.db.backends.sqlite3":
            db_name = unquote(parsed.path or "").lstrip("/")
            name = BASE_DIR / db_name if db_name and not Path(db_name).is_absolute() else Path(db_name or BASE_DIR / "db.sqlite3")
            return {
                "ENGINE": engine,
                "NAME": name,
            }

        options = {
            key: values[-1] if len(values) == 1 else values
            for key, values in parse_qs(parsed.query).items()
        }
        config: dict[str, object] = {
            "ENGINE": engine,
            "NAME": unquote((parsed.path or "").lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
            "CONN_MAX_AGE": conn_max_age,
        }
        if options:
            config["OPTIONS"] = options
        return config

    engine = env("DB_ENGINE", "django.db.backends.sqlite3") or "django.db.backends.sqlite3"
    if engine == "django.db.backends.sqlite3":
        return {
            "ENGINE": engine,
            "NAME": env_path("DB_NAME", "db.sqlite3"),
        }

    return {
        "ENGINE": engine,
        "NAME": env("DB_NAME", required=True),
        "USER": env("DB_USER", ""),
        "PASSWORD": env("DB_PASSWORD", ""),
        "HOST": env("DB_HOST", ""),
        "PORT": env("DB_PORT", ""),
        "CONN_MAX_AGE": conn_max_age,
    }


DEBUG = env_bool("DEBUG", True)

DEFAULT_SECRET_KEY = "change-this-secret-key-before-production"
SECRET_KEY = env("DJANGO_SECRET_KEY", DEFAULT_SECRET_KEY) or DEFAULT_SECRET_KEY
if not DEBUG and SECRET_KEY == DEFAULT_SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "app.middleware.UserLanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "journal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.app_i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "journal.wsgi.application"
ASGI_APPLICATION = "journal.asgi.application"


DATABASES = {
    "default": build_database_config(),
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", "fr") or "fr"

LANGUAGES = [
    ("fr", "Francais"),
    ("en", "English"),
]

TIME_ZONE = env("DJANGO_TIME_ZONE", "Africa/Brazzaville") or "Africa/Brazzaville"

USE_I18N = True
USE_TZ = True


STATIC_URL = env("STATIC_URL", "/static/") or "/static/"
STATIC_ROOT = env_path("STATIC_ROOT", "staticfiles")
APP_STATIC_VERSION = env("APP_STATIC_VERSION", "20260407-1") or "20260407-1"
MEDIA_URL = env("MEDIA_URL", "/media/") or "/media/"
MEDIA_ROOT = env_path("MEDIA_ROOT", "media")


LOGIN_URL = "app:login"
LOGIN_REDIRECT_URL = "app:dashboard"
LOGOUT_REDIRECT_URL = "app:login"
LANGUAGE_COOKIE_AGE = 31536000

APP_TRANSLATION_PROVIDER = (env("APP_TRANSLATION_PROVIDER", "google_free") or "google_free").strip().lower()

SESSION_COOKIE_SAMESITE = env("SESSION_COOKIE_SAMESITE", "Lax") or "Lax"
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", "Lax") or "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

if env_bool("USE_X_FORWARDED_PROTO", not DEBUG):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)
else:
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
