from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Partner(models.Model):
    """Элемент торговой сети: завод, розничная сеть или ИП."""

    name = models.CharField(max_length=255, help_text="Название партнёра")
    email = models.EmailField(db_index=True, help_text="Email для связи")
    country = models.CharField(max_length=100, help_text="Страна, где расположен партнёр")
    city = models.CharField(max_length=100, help_text="Город, где расположен партнёр")
    street = models.CharField(max_length=100, help_text="Улица партнёра")
    house_number = models.CharField(max_length=10, help_text="Номер дома")

    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients",
        help_text="Поставщик — другой элемент сети, от которого получаются товары",
    )

    debt_to_supplier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Сумма задолженности перед поставщиком",
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата и время создания записи")

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(check=Q(debt_to_supplier__gte=0), name="debt_non_negative"),
        ]
        indexes = [
            models.Index(fields=["city", "name"]),
        ]

    def __str__(self):
        """Возвращает название партнёра."""
        return self.name

    @property
    def level(self) -> int:
        """Рассчитывает уровень в иерархии: 0 — завод, 1+ — по цепочке поставщиков."""
        level = 0
        supplier = self.supplier
        while supplier:
            level += 1
            supplier = supplier.supplier
        return level

    def clean(self):
        if self.pk and self.supplier_id == self.pk:
            raise ValidationError("Партнёр не может быть своим собственным поставщиком.")

        seen = set()
        supplier = self.supplier
        level = 0
        while supplier:
            if supplier.pk in seen:
                raise ValidationError("Обнаружен цикл в цепочке поставщиков.")
            seen.add(supplier.pk)
            level += 1
            if level > 2:
                raise ValidationError("Иерархия не должна быть глубже 3 уровней.")
            supplier = supplier.supplier

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Product(models.Model):
    """Продукт, продаваемый участником сети."""

    name = models.CharField(max_length=255, help_text="Название продукта")
    model = models.CharField(max_length=100, help_text="Модель устройства")
    release_date = models.DateField(help_text="Дата выхода продукта на рынок")

    partner = models.ForeignKey(
        "Partner", on_delete=models.CASCADE, related_name="products", help_text="Партнёр, у которого продаётся продукт"
    )

    def __str__(self):
        """Название и модель продукта."""
        return f"{self.name} ({self.model})"
