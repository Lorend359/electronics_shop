from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from .models import Partner, Product


@admin.action(description="Очистить задолженность перед поставщиком")
def clear_debt_to_supplier(modeladmin, request, queryset):
    """Admin action: обнуляет задолженность у выбранных партнёров."""
    queryset.update(debt_to_supplier=0.00)


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
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            func, name, _ = actions['delete_selected']
            actions['delete_selected'] = (func, name, 'Удалить выбранных партнёров')
        return actions


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение продуктов в админке."""
    list_display = ("name", "model", "release_date", "partner")
    list_filter = ("release_date", "partner__city")
    search_fields = ("name", "model")
