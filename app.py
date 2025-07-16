import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import numpy as np

# Configuración de la página

st.set_page_config(
page_title=“💰 Análisis de Gastos Personales”,
page_icon=“💰”,
layout=“wide”,
initial_sidebar_state=“expanded”
)

# CSS personalizado para mejorar la apariencia

st.markdown(”””

<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .section-header {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #d63384;
        margin: 1rem 0;
    }
</style>

“””, unsafe_allow_html=True)

# Función para traer los datos desde Firebase con manejo de errores mejorado

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_datos():
“”“Obtiene los datos desde Firebase con manejo de errores mejorado”””
try:
url = “https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json”
respuesta = requests.get(url, timeout=10)
respuesta.raise_for_status()
datos = respuesta.json()

```
    if datos is None:
        return pd.DataFrame()
    
    # Convertir el JSON a DataFrame
    registros = []
    for id_gasto, gasto in datos.items():
        registros.append({
            "id": id_gasto,
            "categoria": gasto.get("categoría", "Sin categoría"),
            "fecha": gasto.get("fecha", ""),
            "monto": float(gasto.get("monto", 0)),
            "nota": gasto.get("nota", "Sin nota")
        })
    
    df = pd.DataFrame(registros)
    
    # Parsear fecha con múltiples formatos
    if not df.empty:
        try:
            df["fecha"] = pd.to_datetime(df["fecha"], format="%d %b %Y, %I:%M %p")
        except ValueError:
            try:
                df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d %H:%M:%S")
            except ValueError:
                df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
    
    return df.dropna(subset=["fecha"])

except requests.exceptions.RequestException as e:
    st.error(f"Error al conectar con la base de datos: {str(e)}")
    return pd.DataFrame()
except Exception as e:
    st.error(f"Error inesperado: {str(e)}")
    return pd.DataFrame()
```

def calcular_estadisticas(df):
“”“Calcula estadísticas avanzadas de los gastos”””
if df.empty:
return {}

```
# Calcular días del período
dias_periodo = (df['fecha'].max() - df['fecha'].min()).days
if dias_periodo == 0:
    dias_periodo = 1

categoria_mayor_gasto = df.groupby('categoria')['monto'].sum()
if not categoria_mayor_gasto.empty:
    categoria_mayor = categoria_mayor_gasto.idxmax()
else:
    categoria_mayor = "Sin categoría"

stats = {
    'total_gastos': df['monto'].sum(),
    'promedio_diario': df['monto'].sum() / dias_periodo,
    'gasto_mayor': df['monto'].max(),
    'gasto_menor': df['monto'].min(),
    'categoria_mayor': categoria_mayor,
    'total_transacciones': len(df),
    'promedio_por_transaccion': df['monto'].mean(),
    'mediana': df['monto'].median(),
    'desviacion_estandar': df['monto'].std()
}

return stats
```

def generar_insights(df, stats):
“”“Genera insights automáticos basados en los datos”””
insights = []

```
if df.empty:
    return insights

# Insight sobre la categoría más costosa
categoria_mayor = df.groupby('categoria')['monto'].sum().sort_values(ascending=False)
if len(categoria_mayor) > 1:
    porcentaje = (categoria_mayor.iloc[0] / categoria_mayor.sum()) * 100
    insights.append(f"💡 **{categoria_mayor.index[0]}** representa el {porcentaje:.1f}% de tus gastos totales")

# Insight sobre frecuencia de gastos
dias_con_gastos = df['fecha'].dt.date.nunique()
dias_periodo = (df['fecha'].max() - df['fecha'].min()).days + 1
porcentaje_dias = (dias_con_gastos / dias_periodo) * 100
insights.append(f"📅 Tienes gastos registrados en {dias_con_gastos} de {dias_periodo} días ({porcentaje_dias:.1f}%)")

# Insight sobre gastos altos
gastos_altos = df[df['monto'] > stats['promedio_por_transaccion'] * 2]
if not gastos_altos.empty:
    insights.append(f"⚠️ Tienes {len(gastos_altos)} gastos superiores al doble del promedio")

return insights
```

def crear_grafico_categoria(df):
“”“Crea un gráfico de barras horizontal para gastos por categoría”””
if df.empty:
return None

```
df_categoria = df.groupby("categoria")["monto"].sum().sort_values(ascending=True)

fig = px.bar(
    x=df_categoria.values,
    y=df_categoria.index,
    orientation='h',
    title="💳 Gastos por Categoría",
    labels={'x': 'Monto Total ($)', 'y': 'Categoría'},
    color=df_categoria.values,
    color_continuous_scale='viridis'
)

fig.update_layout(
    height=400,
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

return fig
```

def crear_grafico_temporal(df):
“”“Crea un gráfico de líneas para gastos por fecha”””
if df.empty:
return None

```
df_diario = df.groupby(df["fecha"].dt.date)["monto"].sum().reset_index()
df_diario.columns = ['fecha', 'monto']

fig = px.line(
    df_diario,
    x='fecha',
    y='monto',
    title="📈 Evolución de Gastos Diarios",
    labels={'fecha': 'Fecha', 'monto': 'Gasto ($)'},
    markers=True
)

fig.update_traces(line_color='#667eea', line_width=3)
fig.update_layout(
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

return fig
```

def crear_grafico_distribucion(df):
“”“Crea un gráfico de distribución de gastos”””
if df.empty:
return None

```
fig = px.histogram(
    df,
    x='monto',
    nbins=20,
    title="📊 Distribución de Montos de Gastos",
    labels={'monto': 'Monto ($)', 'count': 'Frecuencia'},
    color_discrete_sequence=['#667eea']
)

fig.update_layout(
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

return fig
```

def crear_grafico_pie(df):
“”“Crea un gráfico circular para distribución por categoría”””
if df.empty:
return None

```
df_categoria = df.groupby("categoria")["monto"].sum()

fig = px.pie(
    values=df_categoria.values,
    names=df_categoria.index,
    title="🥧 Distribución Porcentual por Categoría",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=400)

return fig
```

# — INTERFAZ PRINCIPAL —

# Header principal

st.markdown(”””

<div class="main-header">
    <h1>💰 Análisis de Gastos Personales</h1>
    <p>Dashboard interactivo para el control de tus finanzas</p>
</div>
""", unsafe_allow_html=True)

# Barra lateral con filtros avanzados

st.sidebar.markdown(”### 🔍 Filtros y Configuración”)

# Botón para actualizar datos

if st.sidebar.button(“🔄 Actualizar Datos”):
st.cache_data.clear()
st.rerun()

# Obtener datos

with st.spinner(“Cargando datos…”):
df_gastos = obtener_datos()

if df_gastos.empty:
st.markdown(”””
<div class="warning-box">
<h3>⚠️ No se encontraron datos</h3>
<p>No hay datos disponibles en la base de datos o hubo un error al cargarlos.</p>
</div>
“””, unsafe_allow_html=True)
st.stop()

# Filtros en la barra lateral

st.sidebar.markdown(”#### 📋 Filtrar por Categoría”)
categorias_disponibles = sorted(df_gastos[“categoria”].unique())
categorias_seleccionadas = st.sidebar.multiselect(
“Selecciona las categorías”,
options=categorias_disponibles,
default=categorias_disponibles,
help=“Selecciona una o más categorías para filtrar”
)

st.sidebar.markdown(”#### 📅 Filtrar por Fecha”)
fecha_min = df_gastos[“fecha”].min().date()
fecha_max = df_gastos[“fecha”].max().date()

# Opciones de rango predefinidas

rango_opciones = {
“Último mes”: datetime.now().date() - timedelta(days=30),
“Últimos 3 meses”: datetime.now().date() - timedelta(days=90),
“Últimos 6 meses”: datetime.now().date() - timedelta(days=180),
“Último año”: datetime.now().date() - timedelta(days=365),
“Personalizado”: None
}

rango_seleccionado = st.sidebar.selectbox(
“Selecciona el período”,
options=list(rango_opciones.keys()),
index=len(rango_opciones) - 1  # Por defecto “Personalizado”
)

if rango_seleccionado == “Personalizado”:
rango_fechas = st.sidebar.date_input(
“Rango de fechas personalizado”,
value=(fecha_min, fecha_max),
min_value=fecha_min,
max_value=fecha_max,
help=“Selecciona el rango de fechas para analizar”
)
else:
fecha_desde = max(rango_opciones[rango_seleccionado], fecha_min)
rango_fechas = (fecha_desde, fecha_max)

# Filtro por monto

st.sidebar.markdown(”#### 💵 Filtrar por Monto”)
monto_min = float(df_gastos[“monto”].min())
monto_max = float(df_gastos[“monto”].max())

# Evitar error si min y max son iguales

if monto_min == monto_max:
monto_max += 1.0

rango_montos = st.sidebar.slider(
“Rango de montos”,
min_value=monto_min,
max_value=monto_max,
value=(monto_min, monto_max),
step=1.0,
help=“Filtra los gastos por rango de montos”
)

# Aplicar filtros

if len(rango_fechas) == 2:
df_filtrado = df_gastos[
(df_gastos[“categoria”].isin(categorias_seleccionadas)) &
(df_gastos[“fecha”].dt.date >= rango_fechas[0]) &
(df_gastos[“fecha”].dt.date <= rango_fechas[1]) &
(df_gastos[“monto”] >= rango_montos[0]) &
(df_gastos[“monto”] <= rango_montos[1])
]
else:
df_filtrado = df_gastos[
(df_gastos[“categoria”].isin(categorias_seleccionadas)) &
(df_gastos[“monto”] >= rango_montos[0]) &
(df_gastos[“monto”] <= rango_montos[1])
]

# Calcular estadísticas

stats = calcular_estadisticas(df_filtrado)

# Métricas principales

st.markdown(”### 📊 Resumen Ejecutivo”)

if not df_filtrado.empty:
col1, col2, col3, col4 = st.columns(4)

```
with col1:
    st.metric(
        "💰 Gasto Total",
        f"${stats['total_gastos']:,.2f}",
        delta=f"Promedio: ${stats['promedio_por_transaccion']:.2f}",
        help="Suma total de todos los gastos filtrados"
    )

with col2:
    st.metric(
        "📊 Transacciones",
        f"{stats['total_transacciones']:,}",
        delta=f"Mediana: ${stats['mediana']:.2f}",
        help="Número total de transacciones"
    )

with col3:
    st.metric(
        "📈 Gasto Diario",
        f"${stats['promedio_diario']:,.2f}",
        delta=f"Máximo: ${stats['gasto_mayor']:.2f}",
        help="Promedio de gasto por día"
    )

with col4:
    st.metric(
        "🏆 Categoría Principal",
        stats['categoria_mayor'],
        delta=f"Mínimo: ${stats['gasto_menor']:.2f}",
        help="Categoría con mayor gasto total"
    )
```

else:
st.info(“No hay datos que mostrar con los filtros seleccionados.”)

# Insights automáticos

insights = generar_insights(df_filtrado, stats)
if insights:
st.markdown(”### 💡 Insights Automáticos”)
for insight in insights:
st.markdown(f”””
<div class="insight-box">
{insight}
</div>
“””, unsafe_allow_html=True)

# Separador

st.markdown(”—”)

# Gráficos

st.markdown(”### 📈 Análisis Visual”)

# Crear pestañas para organizar los gráficos

tab1, tab2, tab3, tab4 = st.tabs([“📊 Por Categoría”, “📈 Temporal”, “📋 Distribución”, “🥧 Circular”])

with tab1:
fig_categoria = crear_grafico_categoria(df_filtrado)
if fig_categoria:
st.plotly_chart(fig_categoria, use_container_width=True)
else:
st.info(“No hay datos para mostrar”)

with tab2:
fig_temporal = crear_grafico_temporal(df_filtrado)
if fig_temporal:
st.plotly_chart(fig_temporal, use_container_width=True)
else:
st.info(“No hay datos para mostrar”)

with tab3:
fig_distribucion = crear_grafico_distribucion(df_filtrado)
if fig_distribucion:
st.plotly_chart(fig_distribucion, use_container_width=True)
else:
st.info(“No hay datos para mostrar”)

with tab4:
fig_pie = crear_grafico_pie(df_filtrado)
if fig_pie:
st.plotly_chart(fig_pie, use_container_width=True)
else:
st.info(“No hay datos para mostrar”)

# Tabla de gastos detallada

st.markdown(”### 📄 Detalle de Gastos”)

if not df_filtrado.empty:
# Configurar la tabla
df_mostrar = df_filtrado.copy()
df_mostrar[“fecha”] = df_mostrar[“fecha”].dt.strftime(”%d/%m/%Y %H:%M”)
df_mostrar[“monto”] = df_mostrar[“monto”].apply(lambda x: f”${x:,.2f}”)

```
# Ordenar por fecha descendente
df_mostrar = df_mostrar.sort_values(by="fecha", ascending=False)

# Mostrar la tabla
st.dataframe(
    df_mostrar[["fecha", "categoria", "monto", "nota"]].rename(columns={
        "fecha": "Fecha",
        "categoria": "Categoría",
        "monto": "Monto",
        "nota": "Nota"
    }),
    use_container_width=True,
    hide_index=True
)

# Resumen de la tabla
st.caption(f"Mostrando {len(df_filtrado)} de {len(df_gastos)} transacciones totales")
```

else:
st.info(“No hay datos que mostrar con los filtros seleccionados.”)

# Exportar datos

st.markdown(”### 📥 Exportar Datos”)

col1, col2 = st.columns(2)

with col1:
if not df_filtrado.empty:
csv = df_filtrado.to_csv(index=False).encode(‘utf-8’)
st.download_button(
label=“📄 Descargar CSV”,
data=csv,
file_name=f’gastos_filtrados_{datetime.now().strftime(”%Y%m%d_%H%M%S”)}.csv’,
mime=‘text/csv’,
help=“Exporta los datos filtrados como archivo CSV”
)

with col2:
if not df_filtrado.empty:
json_data = df_filtrado.to_json(orient=‘records’, date_format=‘iso’)
st.download_button(
label=“📋 Descargar JSON”,
data=json_data,
file_name=f’gastos_filtrados_{datetime.now().strftime(”%Y%m%d_%H%M%S”)}.json’,
mime=‘application/json’,
help=“Exporta los datos filtrados como archivo JSON”
)

# Footer

st.markdown(”—”)
st.markdown(”””

<div style="text-align: center; color: #666; padding: 1rem;">
    <p>💰 Análisis de Gastos Personales | Desarrollado con Streamlit</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)