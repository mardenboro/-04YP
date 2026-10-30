from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalog.models import Instrument
from apps.clients.models import Client


class Order(models.Model):
    """Заказ: покупка, прокат или ремонт инструмента."""

    class OrderType(models.TextChoices):
        PURCHASE = "purchase", "Покупка"
        RENTAL = "rental", "Прокат"
        REPAIR = "repair", "Ремонт"

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name="orders", verbose_name="Клиент",
    )
    instrument = models.ForeignKey(
        Instrument, on_delete=models.PROTECT,
        related_name="orders", verbose_name="Инструмент",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="orders", verbose_name="Менеджер",
    )
    order_type = models.CharField("Тип", max_length=20, choices=OrderType.choices)
    total_amount = models.DecimalField("Сумма, ₽", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    completed_at = models.DateTimeField("Завершён", null=True, blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk} — {self.client.full_name}"

    def save(self, *args, **kwargs):
        """
        Каскад при создании: покупка — инструмент бронируется,
        прокат — инструмент уходит в прокат.
        """
        if not self.pk and self.instrument.status == Instrument.Status.AVAILABLE:
            if self.order_type == self.OrderType.PURCHASE:
                self.instrument.status = Instrument.Status.RESERVED
                self.instrument.save()
            elif self.order_type == self.OrderType.RENTAL:
                self.instrument.status = Instrument.Status.RENTED
                self.instrument.save()
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status in (self.Status.NEW, self.Status.CONFIRMED)

    def complete(self):
        """Завершить заказ с каскадом: покупка — продан, прокат — инструмент вернули."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if self.order_type == self.OrderType.PURCHASE:
            self.instrument.status = Instrument.Status.SOLD
            self.instrument.save()
        elif self.order_type == self.OrderType.RENTAL:
            self.instrument.status = Instrument.Status.AVAILABLE
            self.instrument.save()
        self.save()

    def cancel(self):
        """Отменить заказ, вернуть инструмент в наличие."""
        self.status = self.Status.CANCELLED
        if self.instrument.status in (Instrument.Status.RESERVED, Instrument.Status.RENTED):
            self.instrument.status = Instrument.Status.AVAILABLE
            self.instrument.save()
        self.save()
