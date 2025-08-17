from django.contrib import admin
from django.urls import path
from monitor import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/ingest/', views.ingest_processes, name='ingest'),
    path('api/latest/', views.latest_snapshot, name='latest_snapshot'),
    path('api/hosts/', views.list_hosts, name='list_hosts'),
]
