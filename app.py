import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from io import BytesIO

# --- Configuración inicial ---
st.set_page_config(
    page_title="Control Financiero",
    layout="wide",
    initial_sidebar_state="collapsed",  # Mejor experiencia móvil sin sidebar abierto
    menu_items={
        'About': "App financiera desarrollada con Python y Streamlit"
    }
)

# --- Inyectar PWA manifest y metatags ---
st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Control Financiero">
<link rel="apple-touch-icon" href="https://yourdomain.com/icon.png ">

<style>
    body {
        font-size: 16px;
    }
    .stButton>button {
        width: 100%;
        font-size: 16px;
        padding: 10px;
    }
    h1, h2, h3 {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Función para obtener datos ---
@st.cache_data(ttl=300)
def obtener_datos():
    try:
        url = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json "
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not datos:
            return pd.DataFrame()
        registros = []
        for key, gasto in datos.items():
            registros.append({
                "Categoría": gasto.get("categoría", "Sin categoría"),
                "Fecha": gasto.get("fecha", ""),
                "Monto": float(gasto.get("monto", 0)),
                "Nota": gasto.get("nota", "")
            })
        df = pd.DataFrame(registros)
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        return df.dropna(subset=["Fecha"])
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

df = obtener_datos()

# --- Título principal ---
st.markdown("<h2 style='color: #2E86AB;'>💼 Control Financiero Personal</h2>", unsafe_allow_html=True)

if df.empty:
    st.info("No hay datos disponibles. Verifica la conexión.")
    st.stop()

# --- Filtros en móvil (sin sidebar) ---
st.markdown("### 🔍 Filtros")
col1, col2 = st.columns(2)
with col1:
    categorias = st.multiselect("Categorías", options=df["Categoría"].unique(), default=df["Categoría"].unique())
with col2:
    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()
    fecha_rango = st.date_input("Rango de fechas", value=(fecha_min, fecha_max))

# --- Aplicar filtros ---
df_filtrado = df[
    (df["Categoría"].isin(categorias)) &
    (df["Fecha"].dt.date >= fecha_rango[0]) &
    (df["Fecha"].dt.date <= fecha_rango[1])
]

# --- Tabs para navegación móvil ---
tab1, tab2, tab3 = st.tabs(["📊 Resumen", "📁 Gráficos", "📄 Detalles"])

with tab1:
    st.subheader("📈 Métricas Clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total", f"${df_filtrado['Monto'].sum():,.2f}")
    col2.metric("Promedio", f"${df_filtrado['Monto'].mean():,.2f}")
    col3.metric("Transacciones", len(df_filtrado))

with tab2:
    st.subheader("Gráfico por Categoría")
    if not df_filtrado.empty:
        gastos_categoria = df_filtrado.groupby("Categoría")["Monto"].sum().sort_values(ascending=False)
        fig = px.bar(
            gastos_categoria,
            x=gastos_categoria.index,
            y=gastos_categoria.values,
            labels={"x": "Categoría", "y": "Monto ($)"},
            color=gastos_categoria.values,
            color_continuous_scale="Blues"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos.")

with tab3:
    st.subheader("Detalles de Transacciones")
    st.dataframe(df_filtrado.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

# --- Exportar a Excel ---
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
        writer.close()
    return output.getvalue()

st.markdown("---")
st.download_button(
    label="📥 Descargar en Excel",
    data=convertir_a_excel(df_filtrado),
    file_name=f"gastos_exportados_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Footer ---
st.markdown("<p style='text-align: center; color: gray;'>App desarrollada con 💻 y Python</p>", unsafe_allow_html=True)
