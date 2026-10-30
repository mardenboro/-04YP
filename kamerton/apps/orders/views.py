from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD для заказов + завершение и отмена с каскадом."""
    queryset = Order.objects.select_related("client", "instrument__brand", "manager").all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "order_type", "client", "manager"]
    search_fields = ["client__full_name", "instrument__model"]
    ordering_fields = ["created_at", "total_amount"]

    def perform_create(self, serializer):
        # Менеджер — тот, кто оформил заказ
        serializer.save(manager=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """POST /api/orders/{id}/complete/ — завершить заказ."""
        order = self.get_object()
        if not order.is_open:
            return Response({"detail": "Заказ уже закрыт"}, status=status.HTTP_400_BAD_REQUEST)
        order.complete()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """POST /api/orders/{id}/cancel/ — отменить заказ."""
        order = self.get_object()
        if not order.is_open:
            return Response({"detail": "Заказ уже закрыт"}, status=status.HTTP_400_BAD_REQUEST)
        order.cancel()
        return Response(OrderSerializer(order).data)
