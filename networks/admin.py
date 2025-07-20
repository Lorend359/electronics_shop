from django.contrib import admin
from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Отображение партнёров в админке."""
    list_display = ("name", "city", "country", "email", "supplier", "debt_to_supplier", "created_at")
    list_filter = ("city",)
    search_fields = ("name", "email", "city")
