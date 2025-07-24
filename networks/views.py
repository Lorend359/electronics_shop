"""DRF-представления для моделей торговой сети."""

from django.db.models import Case, IntegerField, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Partner
from .serializers import PartnerSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    """CRUD-доступ к партнёрам сети."""

    level_case = Case(
        When(supplier__isnull=True, then=Value(0)),
        When(supplier__supplier__isnull=True, then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )

    queryset = (
        Partner.objects.select_related("supplier", "supplier__supplier")
        .prefetch_related("products")
        .annotate(db_level=level_case)
    )

    serializer_class = PartnerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country"]
