from rest_framework.response import Response
from rest_framework.views import APIView

from .services import ReportService


def int_param(request, name, default):
    """Целый параметр из ?name=..., при мусоре — значение по умолчанию."""
    try:
        return max(1, int(request.GET.get(name, default)))
    except ValueError:
        return default


class KPIApiView(APIView):
    """GET /api/reports/kpi/?days=30"""
    def get(self, request):
        return Response(ReportService.kpi(int_param(request, "days", 30)))


class RevenueByDayApiView(APIView):
    """GET /api/reports/revenue/?days=30"""
    def get(self, request):
        return Response(ReportService.revenue_by_day(int_param(request, "days", 30)))


class TopModelsApiView(APIView):
    """GET /api/reports/top-models/?limit=5"""
    def get(self, request):
        return Response(ReportService.top_models(int_param(request, "limit", 5)))


class ManagerLoadApiView(APIView):
    """GET /api/reports/manager-load/?days=30"""
    def get(self, request):
        return Response(ReportService.manager_load(int_param(request, "days", 30)))


class StockApiView(APIView):
    """GET /api/reports/stock/"""
    def get(self, request):
        return Response(ReportService.stock_status())
