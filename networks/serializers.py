from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Partner, Product


class ProductSerializer(serializers.ModelSerializer):
    """Продукт партнёра (чтение/запись)."""

    class Meta:
        model = Product
        fields = ("id", "name", "model", "release_date", "partner")
        read_only_fields = ("id",)


class PartnerSerializer(serializers.ModelSerializer):
    """
    Партнёр сети (завод / розница / ИП).
    Реализует вложенный вывод продуктов, уровень и ограничения иерархии.
    """
    level = serializers.IntegerField(source="db_level", read_only=True)
    products = ProductSerializer(many=True, read_only=True, help_text="Продукты партнёра.")

    class Meta:
        model = Partner
        fields = (
            "id", "name", "email", "country", "city", "street", "house_number",
            "supplier", "debt_to_supplier", "created_at", "level", "products"
        )
        read_only_fields = ("id", "created_at", "debt_to_supplier")
        extra_kwargs = {
            "supplier": {"required": False, "allow_null": True}
        }

    def validate(self, attrs):
        """
        Валидируем бизнес-логику через clean() модели:
        - отсутствие циклов
        - не глубже 3 уровней
        """
        instance = self.instance or Partner()
        for field, value in attrs.items():
            setattr(instance, field, value)
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)
        return attrs
