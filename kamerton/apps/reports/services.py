from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.catalog.models import Instrument
from apps.orders.models import Order


class ReportService:
    """Сервис отчётов."""

    @staticmethod
    def _completed_sales(days):
        """Завершённые покупки за последние days дней."""
        since = timezone.now() - timedelta(days=days)
        return Order.objects.filter(
            order_type=Order.OrderType.PURCHASE,
            status=Order.Status.COMPLETED,
            completed_at__gte=since,
        )

    @staticmethod
    def kpi(days: int = 30) -> dict:
        """Главные KPI."""
        completed = ReportService._completed_sales(days)
        revenue = completed.aggregate(total=Sum("total_amount"))["total"] or 0
        count = completed.count()
        return {
            "revenue": float(revenue),
            "sales_count": count,
            "avg_check": float(revenue) / count if count else 0,
            "in_stock": Instrument.objects.filter(status=Instrument.Status.AVAILABLE).count(),
            "in_rent": Instrument.objects.filter(status=Instrument.Status.RENTED).count(),
            "period_days": days,
        }

    @staticmethod
    def revenue_by_day(days: int = 30) -> list:
        """Выручка по дням."""
        rows = (
            ReportService._completed_sales(days)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(total=Sum("total_amount"))
            .order_by("day")
        )
        return [{"date": str(r["day"]), "total": float(r["total"])} for r in rows]

    @staticmethod
    def top_models(limit: int = 5) -> list:
        """Топ продаваемых моделей."""
        rows = (
            Order.objects.filter(
                order_type=Order.OrderType.PURCHASE,
                status=Order.Status.COMPLETED,
            )
            .values("instrument__brand__name", "instrument__model")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
        return [
            {"brand": r["instrument__brand__name"], "model": r["instrument__model"], "count": r["count"]}
            for r in rows
        ]

    @staticmethod
    def manager_load(days: int = 30) -> list:
        """Загрузка менеджеров: сколько заказов оформил каждый."""
        since = timezone.now() - timedelta(days=days)
        rows = (
            Order.objects.filter(created_at__gte=since)
            .values("manager__username")
            .annotate(count=Count("id"), total=Sum("total_amount"))
            .order_by("-count")
        )
        return [
            {"manager": r["manager__username"], "orders": r["count"], "total": float(r["total"] or 0)}
            for r in rows
        ]

    @staticmethod
    def stock_status() -> list:
        """Состояние склада."""
        return [
            {"status": r["status"], "count": r["count"]}
            for r in Instrument.objects.values("status").annotate(count=Count("id")).order_by("status")
        ]
