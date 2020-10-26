"""
Django settings for homePIX project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join( BASE_DIR, 'homePIX/templates' )
MEDIA_ROOT = os.path.abspath( '/home/ElliottCB/pictures' )
MEDIA_URL  = '/media/'
REMOTE_URLs  = [
    'https://api.smugmug.com/services/api/json/1.3.0/',
    ]
REMOTE_CMDs  = [
    'smugmug.albums.get',
    ]
REMOTE_PARAMs  = [
    'APIKey=S5fXMcQLW98ZddrcqVZFMsbJ3GfvfS3m&NickName=elliottbignell',
    ]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$2z$r*$o-d^9x(8u^wiwv^o32b_k7rc=c1^-%5!1$iv$&#jzri'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '192.168.1.110',
    'elliottcb.pythonanywhere.com'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#   'django_bootstrap_breadcrumbs',
#    'background_task',
    'homePIX',
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

ROOT_URLCONF = 'homePIX.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ TEMPLATE_DIR, ],
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

WSGI_APPLICATION = 'homePIX.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join( BASE_DIR, 'static' )

LOGIN_REDIRECT_URL = '/'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECUR = True

STATICFILES_DIRS = (

    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/ElliottCB/homePIX/static/',
)

# Default settings
BOOTSTRAP3 = {

    # The complete URL to the Bootstrap CSS file
    # Note that a URL can be either
    # - a string, e.g. "//code.jquery.com/jquery.min.js"
    # - a dict like the default value below (use key "url" for the actual link)
    "css_url": {
        "url": "https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css",
        "integrity": "sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu",
        "crossorigin": "anonymous",
    },

    # The complete URL to the Bootstrap CSS file (None means no theme)
    "theme_url": None,

    # The complete URL to the Bootstrap JavaScript file
    "javascript_url": {
        "url": "https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js",
        "integrity": "sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd",
        "crossorigin": "anonymous",
    },

    # The URL to the jQuery JavaScript file
    "jquery_url": "http://code.jquery.com/jquery.min.js",

    # Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
    "javascript_in_head": False,

    # Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
    "include_jquery": True,

    # Label class to use in horizontal forms
    "horizontal_label_class": "col-md-3",

    # Field class to use in horizontal forms
    "horizontal_field_class": "col-md-9",

    # Set placeholder attributes to label if no placeholder is provided.
    # This also considers the "label" option of {% bootstrap_field %} tags.
    "set_placeholder": True,

    # Class to indicate required (better to set this in your Django form)
    "required_css_class": "",

    # Class to indicate error (better to set this in your Django form)
    "error_css_class": "has-error",

    # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
    "success_css_class": "has-success",

    # Renderers (only set these if you have studied the source and understand the inner workings)
    "formset_renderers":{
        "default": "bootstrap3.renderers.FormsetRenderer",
    },
    "form_renderers": {
        "default": "bootstrap3.renderers.FormRenderer",
    },
    "field_renderers": {
        "default": "bootstrap3.renderers.FieldRenderer",
        "inline": "bootstrap3.renderers.InlineFieldRenderer",
    },
}