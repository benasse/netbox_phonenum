from netbox.search import SearchIndex

from .models import Number, Pool, VoiceCircuit


class PoolIndex(SearchIndex):
    model = Pool
    fields = (
        ("name", 100),
        ("start", 100),
        ("end", 100),
        ("description", 500),
    )
    display_attrs = ("start", "end", "tenant", "site", "provider", "description")


class NumberIndex(SearchIndex):
    model = Number
    fields = (
        ("name", 100),
        ("description", 500),
    )
    display_attrs = ("pool", "is_used", "description")


class VoiceCircuitIndex(SearchIndex):
    model = VoiceCircuit
    fields = (
        ("name", 100),
        ("provider_circuit_id", 200),
        ("description", 500),
        ("sip_source", 500),
        ("sip_target", 500),
    )
    display_attrs = ("voice_circuit_type", "tenant", "site", "provider", "provider_circuit_id")


indexes = [PoolIndex, NumberIndex, VoiceCircuitIndex]
