from rest_framework import serializers
from .models import Host, Snapshot, Process

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['pid', 'ppid', 'name', 'cpu_percent', 'memory_mb']

class SnapshotSerializer(serializers.ModelSerializer):
    processes = serializers.SerializerMethodField()

    class Meta:
        model = Snapshot
        fields = ['id', 'created_at', 'processes']

    def get_processes(self, obj):
        processes = obj.processes.all().order_by('-cpu_percent')  # descending order
        return ProcessSerializer(processes, many=True).data

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['id', 'hostname']
