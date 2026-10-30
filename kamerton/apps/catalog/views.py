"""ViewSet автоматически создаёт все CRUD-эндпоинты:
  GET    /api/instruments/        — список
  POST   /api/instruments/        — создать
  GET    /api/instruments/{id}/   — детали
  PUT    /api/instruments/{id}/   — обновить
  DELETE /api/instruments/{id}/   — удалить
  PATCH  /api/instruments/{id}/status/ — сменить статус"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Brand, Instrument
from .serializers import BrandSerializer, InstrumentSerializer, InstrumentStatusSerializer


class BrandViewSet(viewsets.ModelViewSet):
    """CRUD для производителей."""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "country"]


class InstrumentViewSet(viewsets.ModelViewSet):
    """CRUD для инструментов с фильтрами."""
    queryset = Instrument.objects.select_related("brand").all()
    serializer_class = InstrumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["brand", "category", "status", "condition", "year"]
    search_fields = ["model", "serial_number", "brand__name"]
    ordering_fields = ["price", "year", "created_at"]

    @action(detail=True, methods=["patch"], serializer_class=InstrumentStatusSerializer)
    def status(self, request, pk=None):
        """Сменить статус инструмента."""
        instrument = self.get_object()
        serializer = InstrumentStatusSerializer(instrument, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InstrumentSerializer(instrument).data)
