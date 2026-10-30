"""МОДУЛЬ 4 (ЗАКАЗЫ): Формы."""

from django import forms

from apps.catalog.models import Instrument

from .models import Order


class OrderForm(forms.ModelForm):
    """Форма создания заказа."""

    class Meta:
        model = Order
        fields = ["client", "instrument", "order_type", "total_amount", "comment"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "instrument": forms.Select(attrs={"class": "form-select"}),
            "order_type": forms.Select(attrs={"class": "form-select"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только доступные инструменты
        self.fields["instrument"].queryset = Instrument.objects.filter(
            status=Instrument.Status.AVAILABLE,
        )
