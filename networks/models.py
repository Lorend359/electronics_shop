from django.db import models


class Partner(models.Model):
    """Элемент торговой сети: завод, розничная сеть или ИП."""

    name = models.CharField(max_length=255, help_text="Название партнёра")
    email = models.EmailField(help_text="Email для связи")
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
        help_text="Поставщик — другой элемент сети, от которого получаются товары"
    )

    debt_to_supplier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Сумма задолженности перед поставщиком"
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата и время создания записи")

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

