import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Análisis de Gastos", layout="wide")

# --- Función para traer los datos desde Firebase ---
@st.cache_data
def obtener_datos():
    url = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"
    respuesta = requests.get(url)
    datos = respuesta.json()
    
    if datos is None:
        return pd.DataFrame()
    
    # Convertir el JSON a DataFrame
    registros = []
    for id_gasto, gasto in datos.items():
        registros.append({
            "id": id_gasto,
            "categoria": gasto.get("categoría", ""),
            "fecha": gasto.get("fecha", ""),
            "monto": float(gasto.get("monto", 0)),
            "nota": gasto.get("nota", "")
        })
    
    df = pd.DataFrame(registros)
    
    # Parsear fecha
    try:
        df["fecha"] = pd.to_datetime(df["fecha"], format="%d %b %Y, %I:%M %p")
    except:
        df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')

    return df.dropna(subset=["fecha"])

# --- Título ---
st.title("📊 Análisis de Gastos Personales")

# --- Obtener datos ---
df_gastos = obtener_datos()

if df_gastos.empty:
    st.warning("No se encontraron datos en la base de datos.")
    st.stop()

# --- Filtros ---
st.sidebar.header("Filtros")
categorias = st.sidebar.multiselect("Categorías", options=df_gastos["categoria"].unique(), default=df_gastos["categoria"].unique())
rango_fechas = st.sidebar.date_input("Rango de fechas", [df_gastos["fecha"].min(), df_gastos["fecha"].max()])

# --- Aplicar filtros ---
df_filtrado = df_gastos[
    (df_gastos["categoria"].isin(categorias)) &
    (df_gastos["fecha"].dt.date >= rango_fechas[0]) &
    (df_gastos["fecha"].dt.date <= rango_fechas[1])
]

# --- Métricas clave ---
col1, col2, col3 = st.columns(3)
col1.metric("💰 Gasto total", f"${df_filtrado['monto'].sum():,.2f}")
col2.metric("📆 Desde", rango_fechas[0].strftime("%d %b %Y"))
col3.metric("📆 Hasta", rango_fechas[1].strftime("%d %b %Y"))

st.markdown("---")

# --- Gráfico por categoría ---
st.subheader("Gasto por Categoría")
df_categoria = df_filtrado.groupby("categoria")["monto"].sum().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(8, 5))
sns.barplot(x=df_categoria.values, y=df_categoria.index, ax=ax1, palette="viridis")
ax1.set_xlabel("Monto Total ($)")
ax1.set_ylabel("Categoría")
st.pyplot(fig1)

# --- Gasto por día ---
st.subheader("Gasto Diario")
df_diario = df_filtrado.groupby(df_filtrado["fecha"].dt.date)["monto"].sum()

fig2, ax2 = plt.subplots(figsize=(10, 4))
df_diario.plot(kind="line", marker="o", ax=ax2)
ax2.set_ylabel("Gasto ($)")
ax2.set_xlabel("Fecha")
ax2.grid(True)
st.pyplot(fig2)

# --- Tabla de gastos ---
st.subheader("📄 Detalle de Gastos")
st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False), use_container_width=True)

# --- Exportar CSV ---
st.subheader("📥 Exportar Datos")

csv = df_filtrado.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇️ Descargar como CSV",
    data=csv,
    file_name='gastos_filtrados.csv',
    mime='text/csv',
    help="Exporta los datos filtrados como archivo CSV"
)