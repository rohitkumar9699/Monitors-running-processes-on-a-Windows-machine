from django.contrib import admin
from .models import Host, Snapshot, Process


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostname', 'created_at')
    search_fields = ('hostname',)


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'created_at')
    list_filter = ('host',)
    search_fields = ('host__hostname',)


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'snapshot', 'name', 'pid', 'ppid', 'cpu_percent', 'memory_mb', 'created_at')
    list_filter = ('snapshot',)
    search_fields = ('name',)
