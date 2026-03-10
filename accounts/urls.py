from django.contrib import admin
from django.urls import re_path as url, include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Repoapp.urls')),
]