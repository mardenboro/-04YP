"""МОДУЛЬ 4 (ЗАКАЗЫ): Админка."""

from django.contrib import admin, messages

from apps.catalog.models import Instrument

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "instrument", "order_type", "total_amount", "status", "created_at")
    list_filter = ("status", "order_type", "created_at")
    search_fields = ("client__full_name", "instrument__model")
    readonly_fields = ("created_at", "completed_at")
    actions = ("complete_orders", "cancel_orders")

    def get_changeform_initial_data(self, request):
        # Менеджер по умолчанию — текущий пользователь
        return {"manager": request.user.pk}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # В новом заказе предлагаем только инструменты в наличии
        if db_field.name == "instrument" and request.resolver_match.url_name.endswith("_add"):
            kwargs["queryset"] = Instrument.objects.filter(status=Instrument.Status.AVAILABLE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.action(description="Завершить выбранные заказы")
    def complete_orders(self, request, queryset):
        done = 0
        for order in queryset:
            if order.is_open:
                order.complete()
                done += 1
        self.message_user(request, f"Завершено заказов: {done}", messages.SUCCESS)

    @admin.action(description="Отменить выбранные заказы")
    def cancel_orders(self, request, queryset):
        done = 0
        for order in queryset:
            if order.is_open:
                order.cancel()
                done += 1
        self.message_user(request, f"Отменено заказов: {done}", messages.SUCCESS)
