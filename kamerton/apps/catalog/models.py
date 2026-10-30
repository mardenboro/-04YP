from django.db import models
from django.urls import reverse


class Brand(models.Model):
    """Производитель инструментов."""
    name = models.CharField("Название", max_length=50, unique=True)
    country = models.CharField("Страна", max_length=50, blank=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Instrument(models.Model):
    """Музыкальный инструмент (конкретный экземпляр на складе)."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "В наличии"
        RESERVED = "reserved", "Забронирован"
        RENTED = "rented", "В прокате"
        SOLD = "sold", "Продан"

    class Category(models.TextChoices):
        GUITAR = "guitar", "Гитара"
        BASS = "bass", "Бас-гитара"
        KEYS = "keys", "Клавишные"
        DRUMS = "drums", "Ударные"
        WIND = "wind", "Духовые"
        STRINGS = "strings", "Смычковые"

    class Condition(models.TextChoices):
        NEW = "new", "Новый"
        USED = "used", "Б/у"

    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT,
        related_name="instruments", verbose_name="Производитель",
    )
    model = models.CharField("Модель", max_length=100)
    category = models.CharField("Категория", max_length=20, choices=Category.choices)
    year = models.PositiveIntegerField("Год выпуска")
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2)
    color = models.CharField("Цвет / отделка", max_length=50, blank=True)
    condition = models.CharField(
        "Состояние", max_length=10,
        choices=Condition.choices, default=Condition.NEW,
    )
    warranty_months = models.PositiveIntegerField("Гарантия, мес.", default=12)
    status = models.CharField(
        "Статус", max_length=20,
        choices=Status.choices, default=Status.AVAILABLE,
    )
    serial_number = models.CharField(
        "Серийный номер", max_length=30, unique=True, blank=True, null=True,
    )
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand.name} {self.model} ({self.year})"

    def get_absolute_url(self):
        return reverse("instruments-detail", args=[self.pk])

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE
