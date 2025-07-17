import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

# SECURITY
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# APPLICATIONS
INSTALLED_APPS = [
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd Party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",

    # Local Apps
    "accounts.apps.AccountsConfig",
    "mpesa.apps.MpesaConfig",
    "loans.apps.LoansConfig",
    "investments.apps.InvestmentsConfig",
    "notifications.apps.NotificationsConfig",
    "admin_panel.apps.AdminPanelConfig",
]

# MIDDLEWARE
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be first for CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.LogAPIErrorsMiddleware",  # Custom logging middleware
]

# URL & WSGI
ROOT_URLCONF = "smartbank.urls"
WSGI_APPLICATION = "smartbank.wsgi.application"

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
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

# DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# AUTHENTICATION
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# STATIC & MEDIA FILES
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# CORS CONFIGURATION
CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
]
# Development only
CORS_ALLOW_ALL_ORIGINS = DEBUG

# REST FRAMEWORK CONFIG
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
}

# JWT CONFIG
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# MPESA SETTINGS
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://yourdomain.com/api/mpesa/callback/")
MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/smartbank_errors.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
        "mpesa": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
