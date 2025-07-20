from django.contrib import admin
from .models import Partner, Product


class ProductInline(admin.TabularInline):
    """Встроенное отображение продуктов в карточке партнёра."""
    model = Product
    extra = 1  # Показывать 1 пустую строку для добавления
    fields = ("name", "model", "release_date")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Отображение партнёров в админке."""
    list_display = ("name", "city", "country", "email", "supplier", "debt_to_supplier", "created_at")
    list_filter = ("city",)
    search_fields = ("name", "email", "city")
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение продуктов в админке."""
    list_display = ("name", "model", "release_date", "partner")
    list_filter = ("release_date", "partner__city")
    search_fields = ("name", "model")
