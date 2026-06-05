from django.db.models import Q
from netbox.plugins import PluginTemplateExtension

from .models import Number, Pool, VoiceCircuit


class TenantPhoneNumberSummary(PluginTemplateExtension):
    models = ["tenancy.tenant"]

    def right_page(self):
        tenant = self.context["object"]
        pools = Pool.objects.filter(tenant=tenant)
        numbers = Number.objects.filter(Q(pool__tenant=tenant) | Q(tenant=tenant)).distinct()
        standalone_numbers = numbers.filter(pool__isnull=True)

        pool_capacity = 0
        for pool in pools:
            pool_capacity += pool.size or 0
        total_number_count = pool_capacity + standalone_numbers.count()

        return self.render(
            "netbox_phonenum/inc/tenant_phone_summary.html",
            extra_context={
                "pool_count": pools.count(),
                "pool_capacity": pool_capacity,
                "number_count": total_number_count,
                "standalone_number_count": standalone_numbers.count(),
                "voice_circuit_count": VoiceCircuit.objects.filter(tenant=tenant).count(),
            },
        )


template_extensions = [TenantPhoneNumberSummary]
