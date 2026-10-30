from rest_framework import serializers

from .models import Brand, Instrument


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "country"]


class InstrumentSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Instrument
        fields = [
            "id", "brand", "brand_name", "model", "category", "category_display",
            "year", "price", "color", "condition", "condition_display",
            "warranty_months", "status", "status_display",
            "serial_number", "description", "created_at",
        ]
        read_only_fields = ["created_at"]


class InstrumentStatusSerializer(serializers.ModelSerializer):
    """Только смена статуса: PATCH /api/instruments/{id}/status/."""

    class Meta:
        model = Instrument
        fields = ["status"]
