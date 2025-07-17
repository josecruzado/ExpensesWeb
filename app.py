import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Control Financiero", layout="wide")

@st.cache_data(ttl=300)
def obtener_datos():
    try:
        url = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if datos is None:
            return pd.DataFrame()
        registros = []
        for _, gasto in datos.items():
            registros.append({
                "Categoría": gasto.get("categoría", "Sin categoría"),
                "Fecha": gasto.get("fecha", ""),
                "Monto": float(gasto.get("monto", 0)),
                "Nota": gasto.get("nota", "")
            })
        df = pd.DataFrame(registros)
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        return df.dropna(subset=["Fecha"])
    except Exception:
        return pd.DataFrame()

df = obtener_datos()

st.title("💼 Control Financiero Personal")

if df.empty:
    st.warning("No se encontraron datos.")
    st.stop()

# --- SIDEBAR: Filtros ---
st.sidebar.header("Filtros")
categorias = st.sidebar.multiselect("Categorías", df["Categoría"].unique(), default=df["Categoría"].unique())

fecha_min = df["Fecha"].min().date()
fecha_max = df["Fecha"].max().date()
fecha_rango = st.sidebar.date_input("Rango de fechas", (fecha_min, fecha_max))

# --- Filtrar datos ---
df_filtrado = df[
    (df["Categoría"].isin(categorias)) &
    (df["Fecha"].dt.date >= fecha_rango[0]) &
    (df["Fecha"].dt.date <= fecha_rango[1])
]

# --- Métricas ---
st.subheader("📊 Resumen General")
col1, col2, col3 = st.columns(3)
col1.metric("Gasto Total", f"${df_filtrado['Monto'].sum():,.2f}")
col2.metric("Promedio por Gasto", f"${df_filtrado['Monto'].mean():,.2f}")
col3.metric("N° de Transacciones", len(df_filtrado))

# --- Gráfico de barras ---
st.subheader("📁 Gastos por Categoría")
if not df_filtrado.empty:
    gastos_categoria = df_filtrado.groupby("Categoría")["Monto"].sum().sort_values()
    fig = px.bar(
        gastos_categoria,
        x=gastos_categoria.values,
        y=gastos_categoria.index,
        orientation="h",
        labels={"x": "Monto ($)", "y": "Categoría"},
        color=gastos_categoria.values,
        color_continuous_scale="viridis"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos para mostrar.")

# --- Tabla de datos ---
st.subheader("📄 Detalle de Transacciones")
st.dataframe(df_filtrado.sort_values("Fecha", ascending=False), use_container_width=True)

# --- Exportar a Excel ---
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
        writer.close()
    return output.getvalue()

st.download_button(
    label="📥 Exportar a Excel",
    data=convertir_a_excel(df_filtrado),
    file_name=f"gastos_exportados_{datetime.now().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
