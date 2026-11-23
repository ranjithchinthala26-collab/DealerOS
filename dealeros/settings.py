from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY="development-only-change-before-deployment"
DEBUG=True
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "dealeros-h373.onrender.com",
]
INSTALLED_APPS=["django.contrib.contenttypes","django.contrib.auth","rest_framework","corsheaders","reconcile"]
MIDDLEWARE=["corsheaders.middleware.CorsMiddleware","django.middleware.common.CommonMiddleware"]
ROOT_URLCONF="dealeros.urls"
TEMPLATES=[]
WSGI_APPLICATION="dealeros.wsgi.application"
DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
CORS_ALLOW_ALL_ORIGINS=True
REST_FRAMEWORK={"DEFAULT_RENDERER_CLASSES":["rest_framework.renderers.JSONRenderer"]}
