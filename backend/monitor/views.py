from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Host, Snapshot, Process
from .serializers import SnapshotSerializer, HostSerializer


def _require_api_key(request):
    """
    Helper function to validate API key from the request.
    - Checks 'X-API-Key' header or 'HTTP_X_API_KEY' (Django's META format).
    - Compares against BACKEND_API_KEY from settings.
    Returns True if valid, False otherwise.
    """
    api_key = request.headers.get('X-API-Key') or request.META.get('HTTP_X_API_KEY')
    if not api_key or api_key != settings.BACKEND_API_KEY:
        return False
    return True


@api_view(['GET'])
def list_hosts(request):
    """
    Returns a list of all registered hosts in the database, ordered by hostname.
    Used for retrieving all available monitored machines.
    """
    hosts = Host.objects.all().order_by('hostname')
    serializer = HostSerializer(hosts, many=True)
    return Response({'hosts': serializer.data})


@api_view(['POST'])
def ingest_processes(request):
    """
    Endpoint to ingest a new process snapshot from a monitoring agent.
    Steps
    1. Validate API key.
    2. Parse hostname, processes list, and optional system_info.
    3. Store a new Snapshot linked to the Host.
    4. Bulk insert all Process records for performance.
    """
    if not _require_api_key(request):
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    hostname = data.get('hostname')
    processes = data.get('processes', [])
    system_info = data.get('system_info')  # Optional

    # Basic validation
    if not hostname or not isinstance(processes, list):
        return Response({'detail': 'hostname and processes[] required'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():  # Ensure all DB writes happen atomically
        # Create or retrieve host
        host, _ = Host.objects.get_or_create(hostname=hostname)

        # Create new snapshot linked to this host
        snapshot = Snapshot.objects.create(host=host, system_info=system_info)

        # Prepare list of Process objects to insert
        objs = []
        for p in processes:
            objs.append(Process(
                snapshot=snapshot,
                pid=p.get('pid'),
                ppid=p.get('ppid'),
                name=p.get('name', str(p.get('pid'))),
                cpu_percent=p.get('cpu_percent'),
                memory_mb=p.get('memory_mb'),
            ))

        # Bulk insert all processes for efficiency
        Process.objects.bulk_create(objs, batch_size=500)

    return Response(
        {'status': 'ok', 'snapshot_id': snapshot.id, 'created_at': snapshot.created_at},
        status=201
    )


@api_view(['GET'])
def latest_snapshot(request):

    # Retrieves the latest snapshot for a given hostname.
    hostname = request.GET.get('hostname')
    if not hostname:
        return Response({'detail': 'hostname query param required'}, status=400)

    try:
        host = Host.objects.get(hostname=hostname)
    except Host.DoesNotExist:
        return Response({'detail': 'host not found'}, status=404)

    snap = host.snapshots.first()

    # Assumes snapshots are ordered with latest first
    if not snap:
        return Response({'detail': 'no snapshots'}, status=404)

    ser = SnapshotSerializer(snap)
    return Response({
        'hostname': host.hostname,
        'system_info': snap.system_info,  # Include saved system info
        'snapshot': ser.data
    })
