from django.db.models import Count, Prefetch, Q

from .models import Pool


def pool_usage_queryset(queryset=None):
    queryset = queryset or Pool.objects.all()

    annotated_children = Pool.objects.annotate(
        child_pool_count=Count("children", distinct=True),
        number_count=Count("numbers", distinct=True),
        used_number_count=Count("numbers", filter=Q(numbers__is_used=True), distinct=True),
    )

    return (
        queryset
        .select_related("parent", "tenant", "site", "region", "provider", "forward_to")
        .prefetch_related("tags", Prefetch("children", queryset=annotated_children))
        .annotate(
            child_pool_count=Count("children", distinct=True),
            number_count=Count("numbers", distinct=True),
            used_number_count=Count("numbers", filter=Q(numbers__is_used=True), distinct=True),
        )
    )
