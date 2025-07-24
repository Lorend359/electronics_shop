from decimal import Decimal
from django.db import transaction
from django.contrib import admin
from .models import Partner, Product

@admin.action(description="Очистить задолженность перед поставщиком")
def clear_debt_to_supplier(modeladmin, request, queryset):
    """Admin action: обнуляет задолженность у выбранных партнёров."""
    with transaction.atomic():
        updated = queryset.update(debt_to_supplier=Decimal("0.00"))
    modeladmin.message_user(request, f"Задолженность обнулена у {updated} партнёров.")


class ProductInline(admin.TabularInline):
    """Встроенное отображение продуктов в карточке партнёра."""
    model = Product
    extra = 1
    fields = ("name", "model", "release_date")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Отображение партнёров в админке."""
    list_display = ("name", "city", "country", "email", "supplier", "debt_to_supplier", "created_at")
    list_filter = ("city",)
    search_fields = ("name", "email", "city")
    inlines = [ProductInline]
    actions = [clear_debt_to_supplier]

    def get_actions(self, request):
        """Переименовываем стандартное действие удаления."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            func, name, _ = actions['delete_selected']
            actions['delete_selected'] = (func, name, 'Удалить выбранных партнёров')
        return actions

    def get_queryset(self, request):
        """Оптимизируем запрос — подгружаем supplier сразу (select_related)."""
        qs = super().get_queryset(request)
        return qs.select_related("supplier")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение продуктов в админке."""
    list_display = ("name", "model", "release_date", "partner")
    list_filter = ("release_date", "partner__city")
    search_fields = ("name", "model")
