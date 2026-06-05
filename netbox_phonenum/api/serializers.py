from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from circuits.api.serializers import ProviderSerializer
from dcim.api.serializers import RegionSerializer, SiteSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model
from ..choices import VOICE_CIRCUIT_ASSIGNMENT_MODELS
from ..models import VoiceCircuit, Pool, Number


class PoolSerializer(NetBoxModelSerializer):
    start = serializers.CharField()
    end = serializers.CharField()
    size = serializers.IntegerField(read_only=True, allow_null=True)
    used_count = serializers.IntegerField(read_only=True)
    utilization = serializers.IntegerField(read_only=True, allow_null=True)
    #parent = serializers.IntegerField(required=False, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Pool.objects.all(),
        required=False,
        allow_null=True
    )
    tenant = TenantSerializer(required=False, allow_null=True, nested=True)
    region = RegionSerializer(required=False, allow_null=True, nested=True)
    site = SiteSerializer(required=False, allow_null=True, nested=True)
    provider = ProviderSerializer(required=False, allow_null=True, nested=True)
    forward_to = serializers.PrimaryKeyRelatedField(queryset=Pool.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Pool
        fields = (
            "id", "name", "url", "parent", "display", "start", "end", "is_used", "size", "used_count", "utilization",
            "tenant", "site", "region", "forward_to", "description", "provider", "tags",
        )
        brief_fields = ("id", "url", "start", "end", "display", "is_used", "size", "used_count", "utilization")

class VoiceCircuitSerializer(NetBoxModelSerializer):

    label = serializers.CharField(source='voice_circuit', read_only=True)
    tenant = TenantSerializer(required=False, allow_null=True, nested=True)
    region = RegionSerializer(required=False, allow_null=True, nested=True)
    site = SiteSerializer(required=False, allow_null=True, nested=True)
    provider = ProviderSerializer(required=False, allow_null=True, nested=True)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(VOICE_CIRCUIT_ASSIGNMENT_MODELS),
        required=False,
        allow_null=True
    )
    pools = serializers.PrimaryKeyRelatedField(
        queryset=Pool.objects.all(),
        many=True,
        required=False
    )
    numbers = serializers.PrimaryKeyRelatedField(
        queryset=Number.objects.all(),
        many=True,
        required=False
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, context=context).data

    class Meta:
        model = VoiceCircuit
        fields = (
            "id", "url", "label", "display", "name", "voice_circuit_type", "tenant", "region", "site", "description",
            'assigned_object_type','assigned_object_id', 'assigned_object',
            "sip_source", "sip_target", "provider", "provider_circuit_id", "simultaneous_calls", "pools", "numbers", "tags",
        )
        brief_fields = ("id", "url", "name", "display")


class NumberSerializer(NetBoxModelSerializer):
    name = serializers.CharField()
    pool = serializers.PrimaryKeyRelatedField(
        queryset=Pool.objects.all(),
        required=False,
        allow_null=True
    )
    tenant = TenantSerializer(required=False, allow_null=True, nested=True)

    class Meta:
        model = Number
        fields = (
            "id", "name", "description", "is_used", "pool", "tenant"
        )
        brief_fields = ("id", "name", "is_used", "tenant")
