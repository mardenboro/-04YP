from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Камертон — администрирование"
admin.site.site_title = "Камертон"
admin.site.index_title = "Музыкальный магазин «Камертон»"

urlpatterns = [
    # Админка Django
    path("admin/", admin.site.urls),

    # === МОДУЛЬ 1: АВТОРИЗАЦИЯ ===
    path("api/auth/", include("apps.accounts.urls")),

    # === МОДУЛЬ 2: КАТАЛОГ ===
    path("api/", include("apps.catalog.urls")),

    # === МОДУЛЬ 3: КЛИЕНТЫ ===
    path("api/clients/", include("apps.clients.urls")),

    # === МОДУЛЬ 4: ЗАКАЗЫ ===
    path("api/orders/", include("apps.orders.urls")),

    # === МОДУЛЬ 5: ОТЧЁТЫ ===
    path("api/reports/", include("apps.reports.urls")),

    # DRF-вход через браузер (для тестирования)
    path("api/drf-login/", include("rest_framework.urls")),
]
