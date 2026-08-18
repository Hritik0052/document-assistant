from pathlib import Path

import dj_database_url

from config.env import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent
app_settings = get_settings()

SECRET_KEY = app_settings.secret_key
DEBUG = app_settings.debug
ALLOWED_HOSTS = app_settings.allowed_hosts_list

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'documents',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ThemeMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.ui',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

if app_settings.database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            app_settings.database_url,
            conn_max_age=0 if 'neon.tech' in app_settings.database_url else 600,
            ssl_require='neon.tech' in app_settings.database_url or 'sslmode=require' in app_settings.database_url,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'documents:library'
LOGOUT_REDIRECT_URL = 'accounts:login'

OPENROUTER_API_KEY = app_settings.openrouter_api_key
OPENROUTER_BASE_URL = app_settings.openrouter_base_url
OPENROUTER_CHAT_MODEL = app_settings.openrouter_chat_model
OPENROUTER_EMBEDDING_MODEL = app_settings.openrouter_embedding_model
LLM_CONFIGURED = app_settings.llm_configured

RAG_CHUNK_TOKENS = app_settings.rag_chunk_tokens
RAG_CHUNK_OVERLAP = app_settings.rag_chunk_overlap
RAG_TOP_K = app_settings.rag_top_k
RAG_MIN_SIMILARITY = app_settings.rag_min_similarity
MAX_UPLOAD_MB = app_settings.max_upload_mb
DEFAULT_THEME = app_settings.default_theme
THEME_CHOICES = ('light', 'dark', 'ocean', 'forest', 'sunset')

ALLOWED_UPLOAD_EXTENSIONS = {'.pdf', '.txt', '.docx'}
EMBEDDING_DIMENSIONS = app_settings.embedding_dimensions
