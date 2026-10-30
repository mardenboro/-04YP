from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, InstrumentViewSet

router = DefaultRouter()
router.register("brands", BrandViewSet, basename="brands")
router.register("instruments", InstrumentViewSet, basename="instruments")

urlpatterns = [
    path("", include(router.urls)),
]
