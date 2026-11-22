from django.urls import path
from reconcile.views import health, compare, reference_data
urlpatterns=[path("api/health/",health),path("api/compare/",compare),path("api/reference-data/",reference_data)]
