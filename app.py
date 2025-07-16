import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuración
FIREBASE_URL = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"

# Mapeo de meses y días en español
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

DIAS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

def get_dia_es(dia_num):
    return DIAS_ES.get(dia_num, "Desconocido")


@st.cache_data
def get_gastos():
    try:
        # Paso 1: Hacer la petición
        response = requests.get(FIREBASE_URL)
        
        if response.status_code != 200:
            st.error(f"❌ Código HTTP {response.status_code} - Error al conectarse a Firebase.")
            return pd.DataFrame()

        data = response.json()

        # Paso 2: Validar que haya datos
        if not isinstance(data, dict) or not data:
            st.warning("⚠️ No hay datos disponibles en Firebase o formato inválido.")
            return pd.DataFrame()

        # Paso 3: Parsear datos
        parsed = []
        for key, value in data.items():
            if not isinstance(value, dict):  # Saltar elementos corruptos
                continue
            parsed.append({
                "ID": key,
                "Nota": value.get("nota", "Sin nota"),
                "Categoría": value.get("categoria", "Sin categoría"),
                "Monto": float(value.get("monto", 0)),
                "FechaTexto": value.get("fecha", "Sin fecha")
            })

        df = pd.DataFrame(parsed)

        if df.empty:
            st.warning("⚠️ Los datos descargados están vacíos.")
            return df

        # Paso 4: Parsear fechas
        def parse_fecha(fecha_str):
            try:
                return datetime.strptime(fecha_str, "%d %b %Y, %I:%M %p")
            except ValueError:
                try:
                    return datetime.strptime(fecha_str, "%d/%m/%Y")
                except ValueError:
                    return pd.NaT

        df['Fecha'] = df['FechaTexto'].apply(parse_fecha)
        df = df[df['Fecha'].notna()]

        # Paso 5: Extraer información adicional
        df['Año'] = df['Fecha'].dt.year
        df['Mes'] = df['Fecha'].dt.month.map(MESES_ES)  # Mes en español (manual)
        df['DiaSemana'] = df['Fecha'].dt.weekday.map(get_dia_es)  # Día de la semana en español
        df['Dia'] = df['Fecha'].dt.day

        return df[['ID', 'Nota', 'Categoría', 'Monto', 'FechaTexto', 'Fecha', 'Año', 'Mes', 'DiaSemana', 'Dia']]

    except Exception as e:
        st.error(f"❌ Error al procesar los gastos: {e}")
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
