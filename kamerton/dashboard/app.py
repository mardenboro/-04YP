import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

STATUS_NAMES = {"available": "В наличии", "reserved": "Забронирован", "rented": "В прокате", "sold": "Продан"}

st.set_page_config(page_title="Камертон — Аналитика", page_icon="🎸", layout="wide")
st.title("🎸 Камертон — Панель руководителя")

# === ВХОД (API отдаёт отчёты только с JWT-токеном) ===
if "token" not in st.session_state:
    with st.form("login"):
        st.subheader("Вход")
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            try:
                r = requests.post(f"{API_URL}/api/auth/login/",
                                  json={"username": username, "password": password}, timeout=10)
            except requests.ConnectionError:
                st.error(f"Сервер {API_URL} недоступен. Запустите python manage.py runserver")
                st.stop()
            if r.ok:
                st.session_state.token = r.json()["access"]
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
    st.stop()

HEADERS = {"Authorization": f"Bearer {st.session_state.token}"}

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.header("⚙️ Фильтры")
    days = st.selectbox("Период", [7, 30, 90, 365], index=1,
                        format_func=lambda x: f"{x} дней")
    if st.button("🔄 Обновить"):
        st.cache_data.clear()
        st.rerun()
    if st.button("Выйти"):
        del st.session_state.token
        st.cache_data.clear()
        st.rerun()


# === ФУНКЦИИ ЗАГРУЗКИ ДАННЫХ ИЗ API ===
@st.cache_data(ttl=60)
def api_get(path, params=None):
    r = requests.get(f"{API_URL}/api/reports/{path}/", params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


# === KPI-ПЛИТКИ ===
kpi = api_get("kpi", {"days": days})
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Выручка", f"{kpi['revenue']:,.0f} ₽".replace(",", " "))
c2.metric("✅ Продаж", kpi["sales_count"])
c3.metric("📈 Средний чек", f"{kpi['avg_check']:,.0f} ₽".replace(",", " "))
c4.metric("🎹 В наличии", kpi["in_stock"])
c5.metric("🔁 В прокате", kpi["in_rent"])

# === ГРАФИК ВЫРУЧКИ ===
st.header("📈 Динамика выручки")
revenue_df = pd.DataFrame(api_get("revenue", {"days": days}))
if not revenue_df.empty:
    fig = px.line(revenue_df, x="date", y="total", markers=True,
                  labels={"date": "Дата", "total": "Выручка, ₽"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("За период продаж нет")

# === 2 КОЛОНКИ ===
col1, col2 = st.columns(2)

with col1:
    st.header("🏆 Топ-5 моделей")
    top = pd.DataFrame(api_get("top-models"))
    if not top.empty:
        fig = px.bar(top, x="count", y="model", color="brand", orientation="h",
                     labels={"count": "Продано", "model": "Модель", "brand": "Производитель"})
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("👥 Загрузка менеджеров")
    managers = pd.DataFrame(api_get("manager-load", {"days": days}))
    if not managers.empty:
        fig = px.pie(managers, values="orders", names="manager")
        st.plotly_chart(fig, use_container_width=True)

# === СКЛАД ===
st.header("📦 Состояние склада")
stock = pd.DataFrame(api_get("stock"))
if not stock.empty:
    stock["status"] = stock["status"].map(STATUS_NAMES)
    fig = px.pie(stock, values="count", names="status", color="status",
                 color_discrete_map={"В наличии": "green", "Забронирован": "orange",
                                     "В прокате": "royalblue", "Продан": "red"})
    st.plotly_chart(fig, use_container_width=True)
