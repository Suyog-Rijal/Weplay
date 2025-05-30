from pathlib import Path
import environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env()
env = environ.Env(
	DEBUG=(bool, False),
	PRODUCTION=(bool, True)
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=False)
PRODUCTION = env('PRODUCTION', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'rest_framework',
	'drf_spectacular',
	'rest_framework_simplejwt',

	'account',

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

ROOT_URLCONF = 'Weplay.urls'

# Custom user model
AUTH_USER_MODEL = 'account.CustomUser'

# Template configuration
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
			],
		},
	},
]

WSGI_APPLICATION = 'Weplay.wsgi.application'

# Database
if PRODUCTION:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': env('DB_NAME'),
			'USER': env('DB_USER'),
			'PASSWORD': env('DB_PASSWORD'),
			'HOST': env('DB_HOST', default='localhost'),
			'PORT': env('DB_PORT', default='5432'),
		}
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': BASE_DIR / 'db.sqlite3',
		}
	}

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
	],
	'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	)
}

# API documentation configuration
SPECTACULAR_SETTINGS = {
	'TITLE': 'WePlay API',
	'VERSION': '1.0.0',
	'SERVE_INCLUDE_SCHEMA': False,
	"SWAGGER_UI_SETTINGS": {
		"persistAuthorization": True,
	},
	'SORT_OPERATIONS': False,

}

# Simple JWT configuration
SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
	'AUTH_HEADER_TYPES': ('Bearer',),
}


if not PRODUCTION:
	EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
	EMAIL_HOST = "smtp.gmail.com"
	EMAIL_PORT = env('EMAIL_PORT', default=587, cast=int)
	EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True, cast=bool)
	EMAIL_HOST_USER = env('EMAIL_HOST_USER')
	EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
	DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
else:
	EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
	DEFAULT_FROM_EMAIL = "Dev <dev@dev.com>"


GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
