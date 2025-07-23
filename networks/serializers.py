"""DRF-сериализаторы для моделей торговой сети."""

from rest_framework import serializers
from .models import Partner, Product


class ProductSerializer(serializers.ModelSerializer):
    """Продукт партнёра (чтение/запись)."""

    class Meta:
        model = Product
        fields = ("id", "name", "model", "release_date", "partner")
        read_only_fields = ("id",)


class PartnerSerializer(serializers.ModelSerializer):
    """Партнёр сети (завод / розница / ИП)."""

    level = serializers.IntegerField(read_only=True, help_text="Уровень в иерархии.")
    products = ProductSerializer(many=True, read_only=True, help_text="Продукты партнёра.")

    class Meta:
        model = Partner
        fields = (
            "id",
            "name",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "supplier",
            "debt_to_supplier",
            "created_at",
            "level",
            "products",
        )
        read_only_fields = ("id", "created_at")

    def update(self, instance, validated_data):
        """Запрещаем менять задолженность через API."""
        validated_data.pop("debt_to_supplier", None)
        return super().update(instance, validated_data)
