from django.contrib import admin

from .models import Brand, Instrument


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "created_at")
    search_fields = ("name",)


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "category", "year", "price", "status", "condition")
    list_filter = ("brand", "category", "status", "condition", "year")
    search_fields = ("model", "serial_number")
    list_editable = ("status",)
