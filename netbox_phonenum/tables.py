import django_tables2 as tables

from netbox.tables import BaseTable, columns
from .models import VoiceCircuit, Pool, Number

ToggleColumn = columns.ToggleColumn


class PoolTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    start = tables.LinkColumn()
    end = tables.LinkColumn()
    is_used = tables.BooleanColumn(verbose_name="Used")
    parent = tables.LinkColumn()
    tenant = tables.LinkColumn()
    region = tables.LinkColumn()

    site = tables.LinkColumn()
    device = tables.LinkColumn()
    provider = tables.LinkColumn()
    forward_to = tables.LinkColumn()
    size = tables.Column(verbose_name="Pool Size", orderable=False)
    used_count = tables.Column(verbose_name="Used", orderable=False)
    utilization = tables.TemplateColumn(
        template_code="""
            {% if record.utilization is not None %}
                <div class="progress">
                    <div class="progress-bar {{ record.utilization_class }}" role="progressbar"
                        style="width: {{ record.utilization }}%"
                        aria-valuenow="{{ record.utilization }}" aria-valuemin="0" aria-valuemax="100">
                        {{ record.utilization }}%
                    </div>
                </div>
            {% else %}
                <span class="text-muted">&mdash;</span>
            {% endif %}
        """,
        orderable=False,
        verbose_name="Utilization",
    )
    tags = columns.TagColumn()

    class Meta(BaseTable.Meta):
        model = Pool
        fields = ('pk', 'name', 'start', 'end', 'is_used', 'parent', 'tenant', 'site', 'region', 'device', 'description', 'provider',
                  'forward_to', 'size', 'used_count', 'utilization', 'tags')
        default_columns = (
            'pk', 'name', 'start', 'end', 'is_used', 'parent', 'tenant', 'site', 'region', 'device',
            'description', 'provider', 'size', 'used_count', 'utilization', 'tags'
        )


class DevicePoolTable(BaseTable):
    number = tables.Column(accessor='start', linkify=True, verbose_name='Number')
    site = tables.LinkColumn()
    region = tables.LinkColumn()
    provider = tables.LinkColumn()
    forward_to = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = Pool
        fields = ('number', 'site', 'region', 'description', 'provider', 'forward_to')


class VoiceCircuitTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    voice_device_or_vm = tables.Column(
        accessor='assigned_object.parent_object',
        linkify=True,
        orderable=False,
        verbose_name='Device/VM'
    )
    voice_circuit_type = tables.LinkColumn()
    description = tables.Column()
    tenant = tables.LinkColumn()
    region = tables.LinkColumn()
    site = tables.LinkColumn()
    provider = tables.LinkColumn()
    simultaneous_calls = tables.Column(verbose_name='Simultaneous Calls')
    tags = columns.TagColumn()

    class Meta(BaseTable.Meta):
        model = VoiceCircuit
        fields = ('pk', 'name', 'voice_device_or_vm', 'voice_circuit_type', 'description', 'tenant', 'region', 'site',
                  'provider', 'simultaneous_calls', 'tags')


class NumberTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    description = tables.LinkColumn()
    is_used = tables.BooleanColumn(verbose_name="Used")
    pool = tables.LinkColumn()
    
    tenant = tables.Column(
        accessor='effective_tenant',
        linkify=True,
        verbose_name='Tenant',
        order_by=('tenant__name', 'pool__tenant__name'),
    )

    site = tables.Column(
        accessor='pool.site',
        linkify=True,
        verbose_name='Site',
        order_by=('pool__site__name',),
    )


    class Meta(BaseTable.Meta):
        model = Number
        fields = ('pk', 'name', 'description', 'is_used', 'pool', 'tenant', 'site')
