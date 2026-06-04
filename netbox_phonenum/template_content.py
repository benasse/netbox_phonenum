from netbox.plugins import PluginTemplateExtension

from .models import Number, Pool, VoiceCircuit


class TenantPhoneNumberSummary(PluginTemplateExtension):
    models = ["tenancy.tenant"]

    def right_page(self):
        tenant = self.context["object"]
        pools = Pool.objects.filter(tenant=tenant)
        numbers = Number.objects.filter(pool__tenant=tenant)

        pool_capacity = 0
        for pool in pools:
            pool_capacity += pool.size or 0

        return self.render(
            "netbox_phonenum/inc/tenant_phone_summary.html",
            extra_context={
                "pool_count": pools.count(),
                "pool_capacity": pool_capacity,
                "number_count": numbers.count(),
                "used_number_count": numbers.filter(is_used=True).count(),
                "voice_circuit_count": VoiceCircuit.objects.filter(tenant=tenant).count(),
            },
        )


template_extensions = [TenantPhoneNumberSummary]
