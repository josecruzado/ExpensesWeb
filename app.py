import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuración
FIREBASE_URL = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"

# Función para obtener gastos desde Firebase Realtime Database
@st.cache_data
def get_gastos():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code != 200:
            st.error("❌ Error al conectarse a Firebase.")
            return pd.DataFrame()

        data = response.json()

        if not data:
            st.warning("⚠️ No hay datos disponibles en Firebase.")
            return pd.DataFrame()

        # Aplanar el JSON (RTDB devuelve un objeto con claves únicas)
        parsed = []
        for key, value in data.items():
            parsed.append({
                "ID": key,
                "Nota": value.get("nota", "Sin nota"),
                "Categoría": value.get("categoria", "Sin categoría"),
                "Monto": float(value.get("monto", 0)),
                "FechaTexto": value.get("fecha", "Sin fecha")
            })

        df = pd.DataFrame(parsed)

        # Convertir FechaTexto a datetime
        def parse_fecha(fecha_str):
            try:
                return datetime.strptime(fecha_str, "%d %b %Y, %I:%M %p")
            except Exception:
                try:
                    return datetime.strptime(fecha_str, "%d/%m/%Y")
                except Exception:
                    return pd.NaT  # Not a Time

        df['Fecha'] = df['FechaTexto'].apply(parse_fecha)

        # Eliminar filas con fecha inválida
        df = df[df['Fecha'].notna()]

        # Extraer información adicional
        df['Año'] = df['Fecha'].dt.year
        df['Mes'] = df['Fecha'].dt.month_name(locale='es_ES.UTF-8')  # Mes en español
        df['DiaSemana'] = df['Fecha'].dt.day_name(locale='es_ES.UTF-8')  # Día de la semana
        df['Dia'] = df['Fecha'].dt.day

        return df[['ID', 'Nota', 'Categoría', 'Monto', 'FechaTexto', 'Fecha', 'Año', 'Mes', 'DiaSemana', 'Dia']]

    except Exception as e:
        st.error(f"❌ No se pudieron cargar los gastos: {e}")
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
