import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from extras.models import TaggedItem
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet
from .choices import VoiceCircuitTypeChoices, VOICE_CIRCUIT_ASSIGNMENT_MODELS

number_validator = RegexValidator(
    r"^\+?[0-9A-D\#\*]*$",
    "Numbers can only contain: leading +, digits 0-9; chars A, B, C, D; # and *"
)

logger = logging.getLogger(__name__)


class Pool(NetBoxModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    start = models.CharField(max_length=32, validators=[number_validator])
    end = models.CharField(max_length=32, validators=[number_validator])
    is_used = models.BooleanField(default=True)
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    provider = models.ForeignKey(
        to="circuits.Provider",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="provider_set"
    )
    region = models.ForeignKey(
        to="dcim.Region",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="region_set"
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="site_set"
    )
    forward_to = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="forward_to_set"
    )

    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['start', 'end', 'is_used', 'tenant', 'site', 'region', 'description', 'provider', 'forward_to']

    class Meta:
        ordering = ['start']
        verbose_name = 'Number Resource Pool'
        verbose_name_plural = 'Number Resource Pools'

    def __str__(self):
        return f"{self.name} ({self.start}-{self.end})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonenum:pool", kwargs={"pk": self.pk})

    @property
    def is_pool(self):
        return self.start != self.end

    @property
    def size(self):
        try:
            start = int(str(self.start).strip())
            end = int(str(self.end).strip())
        except (TypeError, ValueError):
            return None

        if start > end:
            return None

        return end - start + 1

    @property
    def used_count(self):
        if hasattr(self, "number_count"):
            number_count = self.number_count
        else:
            number_count = self.numbers.count()

        if hasattr(self, "child_pool_count"):
            child_pool_count = self.child_pool_count
        else:
            child_pool_count = self.children.count()

        if self.is_used and child_pool_count == 0 and number_count == 0:
            return self.size or 0

        if hasattr(self, "used_number_count"):
            used_numbers = self.used_number_count
        else:
            used_numbers = self.numbers.filter(is_used=True).count()

        used_children = 0
        children = self._prefetched_objects_cache.get("children") if hasattr(self, "_prefetched_objects_cache") else None
        if children is None:
            children = self.children.all()

        for child in children:
            if child.is_used:
                used_children += child.size or 0
            else:
                used_children += child.used_count

        return used_numbers + used_children

    @property
    def utilization(self):
        size = self.size
        if not size:
            return None

        return min(round((self.used_count / size) * 100), 100)

    @property
    def utilization_class(self):
        utilization = self.utilization
        if utilization is None:
            return ""

        if utilization >= 90:
            return "bg-danger"
        if utilization >= 80:
            return "bg-warning"

        return "bg-success"

    def clean(self):
        if self.start > self.end:
            raise ValidationError("Start must be less than or equal to end.")

        if self.parent and not self.is_pool:
            raise ValidationError("Cannot be assigned to parent is not a pool.")

        overlapping = Pool.objects.filter(
            parent=self.parent,
            start__lte=self.end,
            end__gte=self.start
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("This pool overlaps with an existing sibling pool.")

    def get_children(self, include_self=False):
        """
        Return all covered Pools in the hierarchy.
        """
        # TODO: use include_self
        return Pool.objects.filter(parent=self.id)

    def get_parent_chain(self):
        """
        Return the parent hierarchy chain for this pool
        """
        parents = []
        current = self.parent
        while current:
            parents.insert(0,current)
            current = current.parent
        return parents

class VoiceCircuit(NetBoxModel):
    """A Voice Circuit represents a single circuit of one of the following types:
    - SIP Trunk.
    - Digital Voice Circuit (BRI/PRI/etc).
    - Analog Voice Circuit (CO lines).
    """

    name = models.CharField(max_length=64)
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    description = models.CharField(max_length=200, blank=True)
    voice_circuit_type = models.CharField(
        max_length=50,
        choices=VoiceCircuitTypeChoices,
        blank=False
    )
    provider = models.ForeignKey(
        to="circuits.Provider",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vc_provider_set"
    )
    provider_circuit_id = models.CharField(
        max_length=50,
        blank=True
    )
    simultaneous_calls = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    region = models.ForeignKey(
        to="dcim.Region",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vc_region_set"
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="vc_site_set"
    )
    tags = TaggableManager(through=TaggedItem)

    sip_source = models.CharField(
        max_length=255,
        blank=True
    )
    sip_target = models.CharField(
        max_length=255,
        blank=True
    )

    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=VOICE_CIRCUIT_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    assigned_object_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )
    pools = models.ManyToManyField(
        Pool,
        blank=True,
        related_name='voice_circuits'
    )
    numbers = models.ManyToManyField(
        'Number',
        blank=True,
        related_name='voice_circuits'
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'name', 'voice_circuit_type', 'tenant', 'region', 'site', 'description', 'provider', 'provider_circuit_id',
        'simultaneous_calls'
    ]

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonenum:voicecircuit", kwargs={"pk": self.pk})


class Number(NetBoxModel):
    name = models.CharField(max_length=32, validators=[number_validator])
    description = models.CharField(max_length=50)
    is_used = models.BooleanField(default=True)

    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,          
        related_name='numbers'
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_phonenum:number", kwargs={"pk": self.pk})
