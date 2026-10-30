import os                                                  # работа с переменными окружения
from datetime import timedelta                             # время жизни JWT-токенов
from pathlib import Path                                   # удобные пути

from dotenv import load_dotenv                             # чтение .env

BASE_DIR = Path(__file__).resolve().parent.parent          # корень проекта

load_dotenv(BASE_DIR / ".env")                             # кладём переменные из .env в окружение

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# ПРИЛОЖЕНИЯ

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # DRF и вспомогательные
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",

    # НАШИ 5 МОДУЛЕЙ
    "apps.accounts",    # Модуль 1: Авторизация
    "apps.catalog",     # Модуль 2: Каталог инструментов
    "apps.clients",     # Модуль 3: Клиенты
    "apps.orders",      # Модуль 4: Заказы
    "apps.reports",     # Модуль 5: Отчёты
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",               # CORS первым
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ШАБЛОНЫ

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],                  # общие шаблоны
        "APP_DIRS": True,                                  # шаблоны приложений (admin, DRF)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# БАЗА ДАННЫХ (PostgreSQL)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "kamerton"),
        "USER": os.getenv("POSTGRES_USER", "kamerton"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "kamerton"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# КЭШ И СЕССИИ (Redis / Memurai)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # сессии — в Redis
SESSION_CACHE_ALIAS = "default"

# АУТЕНТИФИКАЦИЯ

AUTH_USER_MODEL = "accounts.User"                          # наша кастомная модель

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# DRF — НАСТРОЙКИ API

REST_FRAMEWORK = {
    # JWT по умолчанию, сессия — для входа в DRF-браузер
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # Только авторизованные (кроме явно открытых)
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    # Фильтрация и поиск
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    # Пагинация
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# JWT — НАСТРОЙКИ ТОКЕНОВ

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS — РАЗРЕШАЕМ STREAMLIT И DESKTOP

CORS_ALLOW_ALL_ORIGINS = True                              # для разработки
# В production: CORS_ALLOWED_ORIGINS = ["http://localhost:8501"]

# ПРОЧЕЕ

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Вход/выход
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"
