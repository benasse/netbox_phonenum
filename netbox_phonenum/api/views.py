from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet
from . import serializers
from .. import filters
from ..models import VoiceCircuit, Pool, Number
from ..querysets import pool_usage_queryset


class phonenumPluginRootView(APIRootView):
    """
    netbox_phonenum API root view
    """
    def get_view_name(self):
        return 'phonenum'

class PoolViewSet(NetBoxModelViewSet):
    queryset = pool_usage_queryset()
    serializer_class = serializers.PoolSerializer
    filterset_class = filters.PoolFilterSet

class VoiceCircuitsViewSet(NetBoxModelViewSet):
    queryset = VoiceCircuit.objects.select_related('tenant', 'region', 'site', 'provider').prefetch_related('pools', 'numbers', 'tags')
    serializer_class = serializers.VoiceCircuitSerializer
    filterset_class = filters.VoiceCircuitFilterSet

class NumberViewSet(NetBoxModelViewSet):
    queryset = Number.objects.select_related('pool', 'pool__tenant', 'pool__site')
    serializer_class = serializers.NumberSerializer
    filterset_class = filters.NumberFilterSet
