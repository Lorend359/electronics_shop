"""DRF-представления для моделей торговой сети."""

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Partner
from .serializers import PartnerSerializer
from .permissions import IsActiveStaff


class PartnerViewSet(viewsets.ModelViewSet):
    """CRUD-доступ к партнёрам сети."""

    queryset = Partner.objects.select_related("supplier").prefetch_related("products").all()
    serializer_class = PartnerSerializer
    permission_classes = [IsActiveStaff]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country"]

    def perform_update(self, serializer):
        """Страховка: даже если сериализатор не убрал долг, не сохраняем его."""

        data = dict(serializer.validated_data)
        data.pop("debt_to_supplier", None)
        serializer.save(**data)
