import django_filters
from django.db.models import Q

from circuits.models import Provider
from dcim.models import Region, Site
from extras.filters import TagFilter
from netbox.filtersets import BaseFilterSet
from tenancy.models import Tenant
from .models import VoiceCircuit, Pool,Number


class PoolFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__id',
        to_field_name='id',
        label='Tenant (id)',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region__id',
        to_field_name='id',
        label='Region (id)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='site__id',
        to_field_name='id',
        label='Site (id)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        field_name='provider__id',
        to_field_name='id',
        label='Region (id)',
    )
    forward_to = django_filters.ModelMultipleChoiceFilter(
        field_name='forward_to',
        queryset=Pool.objects.all(),
        to_field_name='pk',
        label='forward_to',
    )
    is_used = django_filters.BooleanFilter(
        field_name='is_used',
        label='Used',
    )
    tags = TagFilter(to_field_name='slug', field_name='tags__slug')

    class Meta():
        model = Pool
        fields = ('end', 'start', 'parent', 'is_used', 'tags')

    def search(self, queryset, start, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(start__icontains=value) | Q(end__icontains=value)
        )


class VoiceCircuitFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    name = django_filters.ModelMultipleChoiceFilter(
        field_name='name',
        queryset=VoiceCircuit.objects.all(),
        to_field_name='name',
        label='name',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__id',
        to_field_name='id',
        label='Tenant (id)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='site__id',
        to_field_name='id',
        label='Site (id)',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region__id',
        to_field_name='id',
        label='Region (id)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        field_name='provider__id',
        to_field_name='id',
        label='Provider (id)',
    )
    tag = TagFilter()

    class Meta():
        model = VoiceCircuit
        fields = ('name',)

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )


class NumberFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    name = django_filters.ModelMultipleChoiceFilter(
        field_name='name',
        queryset=Number.objects.all(),
        to_field_name='name',
        label='name',
    )
    is_used = django_filters.BooleanFilter(
        field_name='is_used',
        label='Used',
    )
    
    pool = django_filters.ModelChoiceFilter(
        field_name='pool',
        queryset=Pool.objects.all(),
        label='Pool',
    )

    tenant = django_filters.ModelMultipleChoiceFilter(
        method='filter_tenant',
        queryset=Tenant.objects.all(),
        to_field_name='id',
        label='Tenant',
    )

    description = django_filters.ModelMultipleChoiceFilter(
        queryset=Number.objects.all(),
        field_name='description',
        to_field_name='description',
        label='description',
    )
    
    pool_id = django_filters.CharFilter(
        method='filter_pool_id',
        label='Pool (IDs)',
    )

    class Meta():
        model = Number
        fields = ('name', 'is_used')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )

    def filter_tenant(self, queryset, name, value):
        tenant_ids = [tenant.pk for tenant in value]

        if not tenant_ids:
            return queryset

        return queryset.filter(
            Q(pool__tenant_id__in=tenant_ids) | Q(tenant_id__in=tenant_ids)
        ).distinct()

    def filter_pool_id(self, queryset, name, value):
        values = self.data.getlist(name) if hasattr(self.data, "getlist") else [value]
        pool_ids = [item for item in values if item not in ("", "null", None)]
        include_null = any(item == "null" for item in values)

        query = Q()
        if pool_ids:
            query |= Q(pool_id__in=pool_ids)
        if include_null:
            query |= Q(pool__isnull=True)

        if not query:
            return queryset

        return queryset.filter(query)
