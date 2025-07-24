from rest_framework import serializers
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
    level = serializers.IntegerField(read_only=True, help_text="Уровень в иерархии.")
    products = ProductSerializer(many=True, read_only=True, help_text="Продукты партнёра.")

    class Meta:
        model = Partner
        fields = (
            "id", "name", "email", "country", "city", "street", "house_number",
            "supplier", "debt_to_supplier", "created_at", "level", "products"
        )
        read_only_fields = ("id", "created_at")

    def validate(self, data):
        """
        Запрещаем:
        - циклы в цепочке поставщиков (A→...→A)
        - иерархию глубже 3 уровней (level > 2)
        """
        supplier = data.get('supplier') or getattr(self.instance, 'supplier', None)
        current_id = self.instance.pk if self.instance else None

        seen = {current_id}
        level = 0

        while supplier:
            if supplier.pk in seen:
                raise serializers.ValidationError("Обнаружен цикл в цепочке поставщиков.")
            seen.add(supplier.pk)
            level += 1
            if level > 2:
                raise serializers.ValidationError("Иерархия не должна быть глубже 3 уровней (завод → сеть → ИП).")
            supplier = supplier.supplier

        return data

    def update(self, instance, validated_data):
        """Запрещаем менять задолженность через API."""
        validated_data.pop("debt_to_supplier", None)
        return super().update(instance, validated_data)
