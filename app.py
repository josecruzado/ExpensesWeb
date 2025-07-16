import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Título e información
st.set_page_config(page_title="💼 Control de Gastos", layout="wide")
st.title("💼 Sistema de Control de Gastos")
st.markdown("Conectado a Firebase Firestore mediante API REST")

# Firebase config - desde secrets.toml o variables de entorno
FIREBASE_URL = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"
#API_KEY = st.secrets["API_KEY"]

# Función para obtener datos
@st.cache_data
def get_gastos():
    try:
        response = requests.get(f"{FIREBASE_URL}")
        if response.status_code != 200:
            st.error("Error al conectarse a Firebase.")
            return pd.DataFrame()

        data = response.json().get("documents", [])
        parsed = []
        for doc in data:
            fields = doc.get("fields", {})
            parsed.append({
                "Nota": fields.get("nota", {}).get("stringValue", "Sin nota"),
                "Categoría": fields.get("categoria", {}).get("stringValue", "Sin categoría"),
                "Monto": float(fields.get("monto", {}).get("doubleValue", 0)),
                "Fecha": fields.get("fecha", {}).get("timestampValue", "Sin fecha")
            })
        return pd.DataFrame(parsed)
    except Exception as e:
        st.error(f"No se pudieron cargar los gastos: {e}")
        return pd.DataFrame()

# Cargar datos
df = get_gastos()

if not df.empty:
    # Mostrar tabla
    st.subheader("📋 Lista de Gastos")
    st.dataframe(df)

    # Análisis
    st.subheader("📊 Análisis de Gastos")
    total = df['Monto'].sum()
    promedio = df['Monto'].mean()
    maximo = df['Monto'].max()
    minimo = df['Monto'].min()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de gastos", f"${total:.2f}")
    col2.metric("Promedio", f"${promedio:.2f}")
    col3.metric("Máximo", f"${maximo:.2f}")
    col4.metric("Mínimo", f"${minimo:.2f}")

    # Gráfico por categorías
    categoria_sum = df.groupby("Categoría")["Monto"].sum()
    st.bar_chart(categoria_sum)

    # Exportar a Excel
    if st.button("📥 Exportar a Excel"):
        df.to_excel("gastos_reporte.xlsx", index=False)
        with open("gastos_reporte.xlsx", "rb") as f:
            st.download_button("⬇️ Descargar Excel", f, file_name="gastos_reporte.xlsx")
else:
    st.warning("No hay datos disponibles.")
