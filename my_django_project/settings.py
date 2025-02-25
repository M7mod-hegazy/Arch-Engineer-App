import os
from pathlib import Path
import time

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '+je#35#djxep*19i)(^rt$k^=josy11ra(92qpd1p0$_x90k^&'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'EngSa3d',
        'USER': 'm7mod',
        'PASSWORD': '275757',
        'HOST': 'localhost',  # IP address of your PostgreSQL server
        'PORT': '5432',  # Default is '5432'
    }
}

ALLOWED_HOSTS = ['*']  # Allows access from any host

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Home',  # Ensure your app is listed here
    'django.contrib.sites',
    #
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_django_project.wsgi.application'
ASGI_APPLICATION = 'my_django_project.asgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'Home/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add a setting to store the CSS version
CSS_VERSION = str(time.time())

# Override the STATICFILES_STORAGE setting
STATICFILES_STORAGE = 'Home.storage.CacheBustingStaticFilesStorage'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')