from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank= True)

    class Meta:
        abstract = True  # Avoid creating a separate table for BaseModel


class Host(BaseModel):
    hostname = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.hostname


class Snapshot(BaseModel):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='snapshots')
    system_info = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']  # Newest first

    def __str__(self):
        return f"{self.host.hostname} @ {self.created_at.isoformat()}"


class Process(BaseModel):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField()
    ppid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    cpu_percent = models.FloatField(null=True, blank=True)
    memory_mb = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['snapshot', 'ppid']),
            models.Index(fields=['snapshot', 'pid']),
        ]

    def __str__(self):
        return f"{self.name} ({self.pid})"
