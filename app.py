import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="💰 Control Financiero Personal",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .success-card {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .budget-card {
        background: linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Función mejorada para obtener datos
@st.cache_data(ttl=300)
def obtener_datos():
    """Obtiene los datos desde Firebase con manejo de errores mejorado"""
    try:
        url = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        
        if datos is None:
            return pd.DataFrame()
        
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
        
        if not df.empty:
            # Múltiples formatos de fecha
            try:
                df["fecha"] = pd.to_datetime(df["fecha"], format="%d %b %Y, %I:%M %p")
            except ValueError:
                try:
                    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d %H:%M:%S")
                except ValueError:
                    df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
            
            # Agregar columnas derivadas
            df['mes'] = df['fecha'].dt.to_period('M')
            df['semana'] = df['fecha'].dt.to_period('W')
            df['dia_semana'] = df['fecha'].dt.day_name()
            df['hora'] = df['fecha'].dt.hour
        
        return df.dropna(subset=["fecha"])
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la base de datos: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return pd.DataFrame()

# Función para calcular estadísticas avanzadas
def calcular_estadisticas_avanzadas(df):
    """Calcula estadísticas financieras avanzadas"""
    if df.empty:
        return {}
    
    # Estadísticas básicas
    total_gastos = df['monto'].sum()
    promedio_transaccion = df['monto'].mean()
    mediana_transaccion = df['monto'].median()
    
    # Análisis temporal
    dias_periodo = (df['fecha'].max() - df['fecha'].min()).days
    if dias_periodo == 0:
        dias_periodo = 1
    
    promedio_diario = total_gastos / dias_periodo
    
    # Análisis por categoría
    gastos_por_categoria = df.groupby('categoria')['monto'].sum().sort_values(ascending=False)
    categoria_mayor = gastos_por_categoria.index[0] if not gastos_por_categoria.empty else "Sin categoría"
    
    # Análisis de concentración (Coeficiente de Gini simplificado)
    montos_ordenados = df['monto'].sort_values()
    n = len(montos_ordenados)
    if n > 1:
        concentracion = (2 * sum((i+1) * monto for i, monto in enumerate(montos_ordenados))) / (n * montos_ordenados.sum()) - (n+1)/n
    else:
        concentracion = 0
    
    # Análisis de volatilidad
    gastos_diarios = df.groupby(df['fecha'].dt.date)['monto'].sum()
    volatilidad = gastos_diarios.std() / gastos_diarios.mean() if gastos_diarios.mean() != 0 else 0
    
    # Tendencia (regresión lineal simple)
    if len(gastos_diarios) > 1:
        x = np.arange(len(gastos_diarios))
        y = gastos_diarios.values
        tendencia = np.polyfit(x, y, 1)[0]  # Pendiente
    else:
        tendencia = 0
    
    return {
        'total_gastos': total_gastos,
        'promedio_diario': promedio_diario,
        'promedio_transaccion': promedio_transaccion,
        'mediana_transaccion': mediana_transaccion,
        'gasto_mayor': df['monto'].max(),
        'gasto_menor': df['monto'].min(),
        'categoria_mayor': categoria_mayor,
        'total_transacciones': len(df),
        'concentracion': concentracion,
        'volatilidad': volatilidad,
        'tendencia': tendencia,
        'gastos_por_categoria': gastos_por_categoria,
        'dias_periodo': dias_periodo
    }

# Función para generar presupuesto sugerido
def generar_presupuesto_sugerido(df):
    """Genera un presupuesto sugerido basado en gastos históricos"""
    if df.empty:
        return {}
    
    # Calcular gastos promedio por categoría en los últimos 30 días
    fecha_limite = df['fecha'].max() - timedelta(days=30)
    df_reciente = df[df['fecha'] >= fecha_limite]
    
    if df_reciente.empty:
        df_reciente = df
    
    gastos_categoria = df_reciente.groupby('categoria')['monto'].sum()
    dias_periodo = (df_reciente['fecha'].max() - df_reciente['fecha'].min()).days
    if dias_periodo == 0:
        dias_periodo = 1
    
    # Calcular presupuesto mensual sugerido (30 días)
    presupuesto_sugerido = {}
    for categoria, gasto_total in gastos_categoria.items():
        gasto_diario = gasto_total / dias_periodo
        presupuesto_mensual = gasto_diario * 30
        presupuesto_sugerido[categoria] = presupuesto_mensual
    
    return presupuesto_sugerido

# Función para análisis de patrones de gasto
def analizar_patrones_gasto(df):
    """Analiza patrones de gasto por día de la semana y hora"""
    if df.empty:
        return {}, {}
    
    # Gastos por día de la semana
    gastos_dia_semana = df.groupby('dia_semana')['monto'].mean()
    
    # Gastos por hora del día
    gastos_hora = df.groupby('hora')['monto'].sum()
    
    return gastos_dia_semana, gastos_hora

# Función para generar alertas inteligentes
def generar_alertas_inteligentes(df, stats):
    """Genera alertas automáticas basadas en análisis de datos"""
    alertas = []
    
    if df.empty:
        return alertas
    
    # Alerta por gastos inusuales
    if stats['gasto_mayor'] > stats['promedio_transaccion'] * 5:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"🚨 Gasto inusual detectado: ${stats['gasto_mayor']:,.2f} (5x el promedio)"
        })
    
    # Alerta por concentración de gastos
    if stats['concentracion'] > 0.7:
        alertas.append({
            'tipo': 'info',
            'mensaje': f"📊 Alta concentración de gastos en pocas categorías (Coef: {stats['concentracion']:.2f})"
        })
    
    # Alerta por volatilidad
    if stats['volatilidad'] > 1.0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"📈 Alta volatilidad en gastos diarios (Coef: {stats['volatilidad']:.2f})"
        })
    
    # Alerta por tendencia creciente
    if stats['tendencia'] > stats['promedio_diario'] * 0.1:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f"📊 Tendencia creciente en gastos (+${stats['tendencia']:.2f}/día)"
        })
    elif stats['tendencia'] < -stats['promedio_diario'] * 0.1:
        alertas.append({
            'tipo': 'success',
            'mensaje': f"✅ Tendencia decreciente en gastos (-${abs(stats['tendencia']):.2f}/día)"
        })
    
    return alertas

# Función para crear dashboard de salud financiera
def crear_dashboard_salud_financiera(df, stats):
    """Crea un dashboard de salud financiera"""
    if df.empty:
        return None
    
    # Métricas de salud financiera
    metricas = {
        'Consistencia': min(100, (1 - stats['volatilidad']) * 100),
        'Diversificación': min(100, (1 - stats['concentracion']) * 100),
        'Control': min(100, 100 - (stats['gasto_mayor'] / stats['total_gastos']) * 100),
        'Tendencia': 50 + min(50, -stats['tendencia'] / stats['promedio_diario'] * 50)
    }
    
    # Crear gráfico radial
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(metricas.values()),
        theta=list(metricas.keys()),
        fill='toself',
        name='Salud Financiera',
        line_color='#667eea'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="🏥 Dashboard de Salud Financiera",
        height=400
    )
    
    return fig, metricas

# Función para predicción de gastos
def predecir_gastos_futuros(df, dias_futuros=30):
    """Predice gastos futuros basado en tendencias históricas"""
    if df.empty:
        return None
    
    # Gastos diarios históricos
    gastos_diarios = df.groupby(df['fecha'].dt.date)['monto'].sum()
    
    if len(gastos_diarios) < 7:  # Necesitamos al menos una semana de datos
        return None
    
    # Regresión lineal simple para tendencia
    x = np.arange(len(gastos_diarios))
    y = gastos_diarios.values
    
    # Ajustar modelo
    coef = np.polyfit(x, y, 1)
    
    # Predecir días futuros
    x_futuro = np.arange(len(gastos_diarios), len(gastos_diarios) + dias_futuros)
    prediccion = np.polyval(coef, x_futuro)
    
    # Crear fechas futuras
    ultima_fecha = gastos_diarios.index[-1]
    fechas_futuras = [ultima_fecha + timedelta(days=i+1) for i in range(dias_futuros)]
    
    return pd.DataFrame({
        'fecha': fechas_futuras,
        'prediccion': prediccion
    })

# Función para análisis de gastos recurrentes
def analizar_gastos_recurrentes(df):
    """Identifica patrones de gastos recurrentes"""
    if df.empty:
        return pd.DataFrame()
    
    # Agrupar por categoría y nota para identificar gastos similares
    gastos_agrupados = df.groupby(['categoria', 'nota']).agg({
        'monto': ['count', 'mean', 'std'],
        'fecha': ['min', 'max']
    }).reset_index()
    
    # Aplanar columnas
    gastos_agrupados.columns = ['categoria', 'nota', 'frecuencia', 'monto_promedio', 'monto_std', 'primera_fecha', 'ultima_fecha']
    
    # Filtrar gastos que aparecen más de una vez
    gastos_recurrentes = gastos_agrupados[gastos_agrupados['frecuencia'] > 1].copy()
    
    if gastos_recurrentes.empty:
        return pd.DataFrame()
    
    # Calcular días entre primera y última ocurrencia
    gastos_recurrentes['dias_periodo'] = (gastos_recurrentes['ultima_fecha'] - gastos_recurrentes['primera_fecha']).dt.days
    gastos_recurrentes['frecuencia_dias'] = gastos_recurrentes['dias_periodo'] / gastos_recurrentes['frecuencia']
    
    # Filtrar gastos verdaderamente recurrentes (con cierta regularidad)
    gastos_recurrentes = gastos_recurrentes[gastos_recurrentes['frecuencia_dias'] < 60].copy()  # Máximo 60 días entre ocurrencias
    
    return gastos_recurrentes.sort_values('frecuencia', ascending=False)

# --- INTERFAZ PRINCIPAL ---

# Header principal mejorado
st.markdown("""
<div class="main-header">
    <h1>💰 Control Financiero Personal Avanzado</h1>
    <p>Dashboard inteligente para el control integral de tus finanzas</p>
</div>
""", unsafe_allow_html=True)

# Barra lateral con filtros avanzados
st.sidebar.markdown("### 🔍 Filtros y Configuración")

# Botón para actualizar datos
if st.sidebar.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# Obtener datos
with st.spinner("Cargando datos..."):
    df_gastos = obtener_datos()

if df_gastos.empty:
    st.markdown("""
    <div class="alert-card">
        <h3>⚠️ No se encontraron datos</h3>
        <p>No hay datos disponibles en la base de datos o hubo un error al cargarlos.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Configuración de análisis
st.sidebar.markdown("#### ⚙️ Configuración de Análisis")
modo_analisis = st.sidebar.selectbox(
    "Modo de análisis",
    ["Básico", "Avanzado", "Predictivo"],
    index=1,
    help="Selecciona el nivel de análisis deseado"
)

# Filtros existentes (mejorados)
st.sidebar.markdown("#### 📋 Filtrar por Categoría")
categorias_disponibles = sorted(df_gastos["categoria"].unique())
categorias_seleccionadas = st.sidebar.multiselect(
    "Selecciona las categorías",
    options=categorias_disponibles,
    default=categorias_disponibles,
    help="Selecciona una o más categorías para filtrar"
)

st.sidebar.markdown("#### 📅 Filtrar por Fecha")
fecha_min = df_gastos["fecha"].min().date()
fecha_max = df_gastos["fecha"].max().date()

# Opciones de rango predefinidas mejoradas
rango_opciones = {
    "Última semana": datetime.now().date() - timedelta(days=7),
    "Último mes": datetime.now().date() - timedelta(days=30),
    "Últimos 3 meses": datetime.now().date() - timedelta(days=90),
    "Últimos 6 meses": datetime.now().date() - timedelta(days=180),
    "Último año": datetime.now().date() - timedelta(days=365),
    "Personalizado": None
}

rango_seleccionado = st.sidebar.selectbox(
    "Selecciona el período",
    options=list(rango_opciones.keys()),
    index=1,  # Por defecto "Último mes"
)

if rango_seleccionado == "Personalizado":
    rango_fechas = st.sidebar.date_input(
        "Rango de fechas personalizado",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        help="Selecciona el rango de fechas para analizar"
    )
else:
    fecha_desde = max(rango_opciones[rango_seleccionado], fecha_min)
    rango_fechas = (fecha_desde, fecha_max)

# Filtro por monto mejorado
st.sidebar.markdown("#### 💵 Filtrar por Monto")
monto_min = float(df_gastos["monto"].min())
monto_max = float(df_gastos["monto"].max())

if monto_min == monto_max:
    monto_max += 1.0

rango_montos = st.sidebar.slider(
    "Rango de montos",
    min_value=monto_min,
    max_value=monto_max,
    value=(monto_min, monto_max),
    step=1.0,
    help="Filtra los gastos por rango de montos"
)

# Aplicar filtros
if len(rango_fechas) == 2:
    df_filtrado = df_gastos[
        (df_gastos["categoria"].isin(categorias_seleccionadas)) &
        (df_gastos["fecha"].dt.date >= rango_fechas[0]) &
        (df_gastos["fecha"].dt.date <= rango_fechas[1]) &
        (df_gastos["monto"] >= rango_montos[0]) &
        (df_gastos["monto"] <= rango_montos[1])
    ]
else:
    df_filtrado = df_gastos[
        (df_gastos["categoria"].isin(categorias_seleccionadas)) &
        (df_gastos["monto"] >= rango_montos[0]) &
        (df_gastos["monto"] <= rango_montos[1])
    ]

# Calcular estadísticas avanzadas
stats = calcular_estadisticas_avanzadas(df_filtrado)

# Alertas inteligentes
alertas = generar_alertas_inteligentes(df_filtrado, stats)

# Mostrar alertas
if alertas:
    st.markdown("### 🚨 Alertas Inteligentes")
    for alerta in alertas:
        if alerta['tipo'] == 'warning':
            st.markdown(f"""
            <div class="alert-card">
                {alerta['mensaje']}
            </div>
            """, unsafe_allow_html=True)
        elif alerta['tipo'] == 'success':
            st.markdown(f"""
            <div class="success-card">
                {alerta['mensaje']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-box">
                {alerta['mensaje']}
            </div>
            """, unsafe_allow_html=True)

# Métricas principales mejoradas
st.markdown("### 📊 Panel de Control Financiero")

if not df_filtrado.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💰 Gasto Total",
            f"${stats['total_gastos']:,.2f}",
            delta=f"${stats['promedio_diario']:,.2f}/día",
            help="Suma total de gastos y promedio diario"
        )
    
    with col2:
        st.metric(
            "📊 Transacciones",
            f"{stats['total_transacciones']:,}",
            delta=f"${stats['promedio_transaccion']:,.2f} prom.",
            help="Número total de transacciones y promedio por transacción"
        )
    
    with col3:
        volatilidad_color = "normal" if stats['volatilidad'] < 0.5 else "inverse"
        st.metric(
            "📈 Volatilidad",
            f"{stats['volatilidad']:.2f}",
            delta=f"Mediana: ${stats['mediana_transaccion']:,.2f}",
            delta_color=volatilidad_color,
            help="Medida de variabilidad en gastos diarios"
        )
    
    with col4:
        concentracion_color = "inverse" if stats['concentracion'] > 0.7 else "normal"
        st.metric(
            "🎯 Concentración",
            f"{stats['concentracion']:.2f}",
            delta=f"Mayor: ${stats['gasto_mayor']:,.2f}",
            delta_color=concentracion_color,
            help="Concentración de gastos en pocas categorías"
        )
    
    with col5:
        tendencia_color = "inverse" if stats['tendencia'] > 0 else "normal"
        st.metric(
            "📊 Tendencia",
            f"${stats['tendencia']:+.2f}/día",
            delta=f"Período: {stats['dias_periodo']} días",
            delta_color=tendencia_color,
            help="Tendencia diaria de crecimiento/decrecimiento"
        )

# Dashboard de salud financiera
if modo_analisis in ["Avanzado", "Predictivo"] and not df_filtrado.empty:
    st.markdown("### 🏥 Dashboard de Salud Financiera")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig_salud, metricas_salud = crear_dashboard_salud_financiera(df_filtrado, stats)
        if fig_salud:
            st.plotly_chart(fig_salud, use_container_width=True)
    
    with col2:
        st.markdown("#### 📋 Interpretación de Métricas")
        
        for metrica, valor in metricas_salud.items():
            if valor >= 80:
                color = "success-card"
                emoji = "✅"
            elif valor >= 60:
                color = "insight-box"
                emoji = "⚠️"
            else:
                color = "alert-card"
                emoji = "🚨"
            
            st.markdown(f"""
            <div class="{color}">
                <strong>{emoji} {metrica}:</strong> {valor:.1f}/100
            </div>
            """, unsafe_allow_html=True)

# Presupuesto sugerido
if modo_analisis in ["Avanzado", "Predictivo"] and not df_filtrado.empty:
    st.markdown("### 💼 Presupuesto Sugerido")
    
    presupuesto_sugerido = generar_presupuesto_sugerido(df_filtrado)
    
    if presupuesto_sugerido:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de presupuesto vs gastos actuales
            categorias = list(presupuesto_sugerido.keys())
            gastos_actuales = [stats['gastos_por_categoria'].get(cat, 0) for cat in categorias]
            presupuesto_vals = list(presupuesto_sugerido.values())
            
            fig_presupuesto = go.Figure()
            fig_presupuesto.add_trace(go.Bar(
                name='Gasto Actual',
                x=categorias,
                y=gastos_actuales,
                marker_color='#ff6b6b'
            ))
            fig_presupuesto.add_trace(go.Bar(
                name='Presupuesto Sugerido',
                x=categorias,
                y=presupuesto_vals,
                marker_color='#51cf66'
            ))
            
            fig_presupuesto.update_layout(
                title="📊 Presupuesto Sugerido vs Gastos Actuales",
                xaxis_title="Categoría",
                yaxis_title="Monto ($)",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_presupuesto, use_container_width=True)
        
        with col2:
            st.markdown("#### 💡 Recomendaciones")
            
            total_presupuesto = sum(presupuesto_sugerido.values())
            total_actual = sum(gastos_actuales)
            
            if total_actual > total_presupuesto:
                st.markdown(f"""
                <div class="alert-card">
                    <strong>🚨 Sobre-gasto detectado</strong><br>
                    Exceso: ${total_actual - total_presupuesto:,.2f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-card">
                    <strong>✅ Dentro del presupuesto</strong><br>
                    Margen: ${total_presupuesto - total_actual:,.2f}
                </div>
                """, unsafe_allow_html=True)
            
            # Recomendaciones por categoría
            for categoria, presupuesto in presupuesto_sugerido.items():
                gasto_actual = stats['gastos_por_categoria'].get(categoria, 0)
                if gasto_actual > presupuesto * 1.2:
                    st.markdown(f"""
                    <div class="budget-card">
                        <strong>⚠️ {categoria}</strong><br>
                        Reducir: ${gasto_actual - presupuesto:,.2f}
                    </div>
                    """, unsafe_allow_html=True)

# Análisis de patrones
if modo_analisis in ["Avanzado", "Predictivo"] and not df_filtrado.empty:
    st.markdown("### 📈 Análisis de Patrones de Gasto")
    
    gastos_dia_semana, gastos_hora = analizar_patrones_gasto(df_filtrado)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not gastos_dia_semana.empty:
            fig_dia = px.bar(
                x=gastos_dia_semana.index,
                y=gastos_dia_semana.values,
                title="📅 Gastos Promedio por Día de la Semana",
                labels={'x': 'Día de la Semana', 'y': 'Gasto Promedio ($)'},
                color=gastos_dia_semana.values,
                color_continuous_scale='viridis'
            )
            fig_dia.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_dia, use_container_width=True)
    
    with col2:
        if not gastos_hora.empty:
            fig_hora = px.line(
                x=gastos_hora.index,
                y=gastos_hora.values,
                title="🕐 Gastos por Hora del Día",
                labels={'x': 'Hora', 'y': 'Gasto Total ($)'},
                markers=True
            )
            fig_hora.update_traces(line_color='#667eea', line_width=3)
            fig_hora.update_layout(height=400)
            st.plotly_chart(fig_hora, use_container_width=True)

# Análisis de gastos recurrentes
if modo_analisis in ["Avanzado", "Predictivo"] and not df_filtrado.empty:
    st.markdown("### 🔄 Análisis de Gastos Recurrentes")
    
    gastos_recurrentes = analizar_gastos_recurrentes(df_filtrado)
    
    if not gastos_recurrentes.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Gastos Recurrentes Identificados")
            
            # Mostrar tabla de gastos recurrentes
            df_mostrar_rec = gastos_recurrentes.copy()
            df_mostrar_rec['monto_promedio'] = df_mostrar_rec['monto_promedio'].apply(lambda x: f"${x:,.2f}")
            df_mostrar_rec['frecuencia_dias'] = df_mostrar_rec['frecuencia_dias'].apply(lambda x: f"{x:.0f} días")
            
            st.dataframe(
                df_mostrar_rec[['categoria', 'nota', 'frecuencia', 'monto_promedio', 'frecuencia_dias']].rename(columns={
                    'categoria': 'Categoría',
                    'nota': 'Descripción',
                    'frecuencia': 'Frecuencia',
                    'monto_promedio': 'Monto Promedio',
                    'frecuencia_dias': 'Cada'
                }),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("#### 💡 Oportunidades de Ahorro")
            
            # Identificar gastos recurrentes más costosos
            gastos_rec_costosos = gastos_recurrentes.nlargest(3, 'monto_promedio')
            
            for _, gasto in gastos_rec_costosos.iterrows():
                ahorro_potencial = gasto['monto_promedio'] * 0.1  # 10% de ahorro potencial
                st.markdown(f"""
                <div class="insight-box">
                    <strong>💰 {gasto['categoria']}</strong><br>
                    Frecuencia: {gasto['frecuencia']} veces<br>
                    Ahorro potencial: ${ahorro_potencial:,.2f}
                </div>
                """, unsafe_allow_html=True)

# Predicción de gastos futuros
if modo_analisis == "Predictivo" and not df_filtrado.empty:
    st.markdown("### 🔮 Predicción de Gastos Futuros")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        dias_prediccion = st.slider(
            "Días a predecir",
            min_value=7,
            max_value=90,
            value=30,
            help="Selecciona el número de días para la predicción"
        )
        
        prediccion_df = predecir_gastos_futuros(df_filtrado, dias_prediccion)
        
        if prediccion_df is not None:
            # Combinar datos históricos y predicción
            gastos_historicos = df_filtrado.groupby(df_filtrado['fecha'].dt.date)['monto'].sum().reset_index()
            gastos_historicos.columns = ['fecha', 'monto']
            gastos_historicos['tipo'] = 'Histórico'
            
            prediccion_df['tipo'] = 'Predicción'
            prediccion_df = prediccion_df.rename(columns={'prediccion': 'monto'})
            
            # Combinar dataframes
            datos_completos = pd.concat([gastos_historicos, prediccion_df], ignore_index=True)
            
            # Crear gráfico
            fig_prediccion = px.line(
                datos_completos,
                x='fecha',
                y='monto',
                color='tipo',
                title=f"📊 Predicción de Gastos - Próximos {dias_prediccion} días",
                labels={'fecha': 'Fecha', 'monto': 'Gasto ($)', 'tipo': 'Tipo'}
            )
            
            fig_prediccion.update_layout(height=400)
            st.plotly_chart(fig_prediccion, use_container_width=True)
    
    with col2:
        if prediccion_df is not None:
            st.markdown("#### 📈 Estadísticas de Predicción")
            
            gasto_predicho_total = prediccion_df['monto'].sum()
            gasto_predicho_diario = prediccion_df['monto'].mean()
            
            st.markdown(f"""
            <div class="metric-card">
                <strong>💰 Gasto Predicho Total</strong><br>
                ${gasto_predicho_total:,.2f}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <strong>📊 Gasto Predicho Diario</strong><br>
                ${gasto_predicho_diario:,.2f}
            </div>
            """, unsafe_allow_html=True)
            
            # Comparar con histórico
            diferencia = gasto_predicho_diario - stats['promedio_diario']
            if diferencia > 0:
                st.markdown(f"""
                <div class="alert-card">
                    <strong>⚠️ Incremento Esperado</strong><br>
                    +${diferencia:,.2f}/día vs histórico
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-card">
                    <strong>✅ Reducción Esperada</strong><br>
                    ${abs(diferencia):,.2f}/día vs histórico
                </div>
                """, unsafe_allow_html=True)

# Gráficos principales mejorados
st.markdown("### 📈 Análisis Visual Avanzado")

# Crear pestañas para organizar los gráficos
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Categorías", "📈 Temporal", "📋 Distribución", "🥧 Circular", "🔄 Comparativo"])

with tab1:
    if not df_filtrado.empty:
        # Gráfico de categorías con evolución temporal
        fig_cat_tiempo = px.bar(
            df_filtrado,
            x='categoria',
            y='monto',
            color='mes',
            title="📊 Gastos por Categoría y Mes",
            labels={'categoria': 'Categoría', 'monto': 'Monto ($)', 'mes': 'Mes'}
        )
        fig_cat_tiempo.update_layout(height=500)
        st.plotly_chart(fig_cat_tiempo, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")

with tab2:
    if not df_filtrado.empty:
        # Gráfico temporal con medias móviles
        gastos_diarios = df_filtrado.groupby(df_filtrado['fecha'].dt.date)['monto'].sum().reset_index()
        gastos_diarios.columns = ['fecha', 'monto']
        
        # Calcular media móvil de 7 días
        gastos_diarios['media_movil_7'] = gastos_diarios['monto'].rolling(window=7, min_periods=1).mean()
        
        fig_temporal = go.Figure()
        
        # Gastos diarios
        fig_temporal.add_trace(go.Scatter(
            x=gastos_diarios['fecha'],
            y=gastos_diarios['monto'],
            mode='lines+markers',
            name='Gastos Diarios',
            line=dict(color='lightblue', width=1),
            opacity=0.7
        ))
        
        # Media móvil
        fig_temporal.add_trace(go.Scatter(
            x=gastos_diarios['fecha'],
            y=gastos_diarios['media_movil_7'],
            mode='lines',
            name='Media Móvil 7 días',
            line=dict(color='#667eea', width=3)
        ))
        
        fig_temporal.update_layout(
            title="📈 Evolución Temporal con Media Móvil",
            xaxis_title="Fecha",
            yaxis_title="Gasto ($)",
            height=400
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")

with tab3:
    if not df_filtrado.empty:
        # Distribución con estadísticas
        fig_dist = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Histograma', 'Box Plot', 'Gastos por Hora', 'Gastos por Día Semana'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Histograma
        fig_dist.add_trace(
            go.Histogram(x=df_filtrado['monto'], nbinsx=20, name='Distribución'),
            row=1, col=1
        )
        
        # Box plot
        fig_dist.add_trace(
            go.Box(y=df_filtrado['monto'], name='Box Plot'),
            row=1, col=2
        )
        
        # Gastos por hora
        gastos_hora = df_filtrado.groupby('hora')['monto'].sum()
        fig_dist.add_trace(
            go.Bar(x=gastos_hora.index, y=gastos_hora.values, name='Por Hora'),
            row=2, col=1
        )
        
        # Gastos por día de la semana
        gastos_dia = df_filtrado.groupby('dia_semana')['monto'].sum()
        fig_dist.add_trace(
            go.Bar(x=gastos_dia.index, y=gastos_dia.values, name='Por Día'),
            row=2, col=2
        )
        
        fig_dist.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")

with tab4:
    if not df_filtrado.empty:
        # Gráfico circular con desglose
        gastos_categoria = df_filtrado.groupby('categoria')['monto'].sum().sort_values(ascending=False)
        
        fig_pie = go.Figure()
        
        fig_pie.add_trace(go.Pie(
            labels=gastos_categoria.index,
            values=gastos_categoria.values,
            hole=0.4,
            textinfo='label+percent',
            textposition='inside'
        ))
        
        fig_pie.update_layout(
            title="🥧 Distribución de Gastos por Categoría",
            height=500,
            annotations=[dict(text=f'Total<br>${gastos_categoria.sum():,.0f}', 
                            x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")

with tab5:
    if not df_filtrado.empty:
        # Análisis comparativo por períodos
        st.markdown("#### 📊 Análisis Comparativo")
        
        # Comparar último mes vs mes anterior
        fecha_corte = df_filtrado['fecha'].max() - timedelta(days=30)
        
        df_ultimo_mes = df_filtrado[df_filtrado['fecha'] >= fecha_corte]
        df_mes_anterior = df_filtrado[
            (df_filtrado['fecha'] >= fecha_corte - timedelta(days=30)) & 
            (df_filtrado['fecha'] < fecha_corte)
        ]
        
        if not df_ultimo_mes.empty and not df_mes_anterior.empty:
            gastos_ultimo = df_ultimo_mes.groupby('categoria')['monto'].sum()
            gastos_anterior = df_mes_anterior.groupby('categoria')['monto'].sum()
            
            # Crear DataFrame comparativo
            comparativo = pd.DataFrame({
                'Último Mes': gastos_ultimo,
                'Mes Anterior': gastos_anterior
            }).fillna(0)
            
            comparativo['Diferencia'] = comparativo['Último Mes'] - comparativo['Mes Anterior']
            comparativo['Cambio %'] = (comparativo['Diferencia'] / comparativo['Mes Anterior'].replace(0, 1)) * 100
            
            fig_comp = go.Figure()
            
            fig_comp.add_trace(go.Bar(
                name='Mes Anterior',
                x=comparativo.index,
                y=comparativo['Mes Anterior'],
                marker_color='lightcoral'
            ))
            
            fig_comp.add_trace(go.Bar(
                name='Último Mes',
                x=comparativo.index,
                y=comparativo['Último Mes'],
                marker_color='lightblue'
            ))
            
            fig_comp.update_layout(
                title="📊 Comparativo: Último Mes vs Mes Anterior",
                xaxis_title="Categoría",
                yaxis_title="Gasto ($)",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Mostrar tabla de cambios
            st.markdown("##### 📈 Cambios por Categoría")
            
            comparativo_mostrar = comparativo.copy()
            comparativo_mostrar['Último Mes'] = comparativo_mostrar['Último Mes'].apply(lambda x: f"${x:,.2f}")
            comparativo_mostrar['Mes Anterior'] = comparativo_mostrar['Mes Anterior'].apply(lambda x: f"${x:,.2f}")
            comparativo_mostrar['Diferencia'] = comparativo_mostrar['Diferencia'].apply(lambda x: f"${x:+,.2f}")
            comparativo_mostrar['Cambio %'] = comparativo_mostrar['Cambio %'].apply(lambda x: f"{x:+.1f}%")
            
            st.dataframe(comparativo_mostrar, use_container_width=True)
        else:
            st.info("No hay suficientes datos para el análisis comparativo")
    else:
        st.info("No hay datos para mostrar")

# Tabla de gastos detallada mejorada
st.markdown("### 📄 Registro Detallado de Gastos")

if not df_filtrado.empty:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Filtros adicionales para la tabla
        busqueda = st.text_input("🔍 Buscar en notas", help="Busca en las notas de los gastos")
        
    with col2:
        orden = st.selectbox(
            "📊 Ordenar por",
            ["Fecha (desc)", "Fecha (asc)", "Monto (desc)", "Monto (asc)", "Categoría"],
            help="Selecciona el criterio de ordenamiento"
        )
    
    # Aplicar filtros de búsqueda
    df_tabla = df_filtrado.copy()
    
    if busqueda:
        df_tabla = df_tabla[df_tabla['nota'].str.contains(busqueda, case=False, na=False)]
    
    # Aplicar ordenamiento
    if orden == "Fecha (desc)":
        df_tabla = df_tabla.sort_values('fecha', ascending=False)
    elif orden == "Fecha (asc)":
        df_tabla = df_tabla.sort_values('fecha', ascending=True)
    elif orden == "Monto (desc)":
        df_tabla = df_tabla.sort_values('monto', ascending=False)
    elif orden == "Monto (asc)":
        df_tabla = df_tabla.sort_values('monto', ascending=True)
    elif orden == "Categoría":
        df_tabla = df_tabla.sort_values('categoria')
    
    # Preparar datos para mostrar
    df_mostrar = df_tabla.copy()
    df_mostrar["fecha"] = df_mostrar["fecha"].dt.strftime("%d/%m/%Y %H:%M")
    df_mostrar["monto"] = df_mostrar["monto"].apply(lambda x: f"${x:,.2f}")
    
    # Mostrar la tabla con paginación
    filas_por_pagina = 20
    total_filas = len(df_mostrar)
    total_paginas = (total_filas - 1) // filas_por_pagina + 1
    
    if total_paginas > 1:
        pagina = st.selectbox(
            f"📄 Página (Total: {total_paginas})",
            range(1, total_paginas + 1),
            help=f"Mostrando {filas_por_pagina} filas por página"
        )
        
        inicio = (pagina - 1) * filas_por_pagina
        fin = inicio + filas_por_pagina
        df_pagina = df_mostrar.iloc[inicio:fin]
    else:
        df_pagina = df_mostrar
    
    st.dataframe(
        df_pagina[["fecha", "categoria", "monto", "nota"]].rename(columns={
            "fecha": "Fecha",
            "categoria": "Categoría",
            "monto": "Monto",
            "nota": "Descripción"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Estadísticas de la tabla
    st.caption(f"Mostrando {len(df_tabla)} de {len(df_gastos)} transacciones totales")
else:
    st.info("No hay datos que mostrar con los filtros seleccionados.")

# Sección de exportación mejorada
st.markdown("### 📥 Exportación y Reportes")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_filtrado.empty:
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Descargar CSV",
            data=csv,
            file_name=f'gastos_detallados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            help="Exporta los datos filtrados como archivo CSV"
        )

with col2:
    if not df_filtrado.empty:
        json_data = df_filtrado.to_json(orient='records', date_format='iso')
        st.download_button(
            label="📋 Descargar JSON",
            data=json_data,
            file_name=f'gastos_detallados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            mime='application/json',
            help="Exporta los datos filtrados como archivo JSON"
        )

with col3:
    if not df_filtrado.empty:
        # Crear reporte resumido
        reporte_resumen = f"""
REPORTE FINANCIERO PERSONAL
===========================
Período: {df_filtrado['fecha'].min().strftime('%d/%m/%Y')} - {df_filtrado['fecha'].max().strftime('%d/%m/%Y')}
Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESUMEN EJECUTIVO
-----------------
• Total de gastos: ${stats['total_gastos']:,.2f}
• Número de transacciones: {stats['total_transacciones']:,}
• Promedio por transacción: ${stats['promedio_transaccion']:,.2f}
• Gasto diario promedio: ${stats['promedio_diario']:,.2f}

ANÁLISIS POR CATEGORÍA
---------------------
"""
        for categoria, monto in stats['gastos_por_categoria'].head(10).items():
            porcentaje = (monto / stats['total_gastos']) * 100
            reporte_resumen += f"• {categoria}: ${monto:,.2f} ({porcentaje:.1f}%)\n"
        
        reporte_resumen += f"""

MÉTRICAS AVANZADAS
------------------
• Volatilidad: {stats['volatilidad']:.2f}
• Concentración: {stats['concentracion']:.2f}
• Tendencia: ${stats['tendencia']:+.2f}/día
• Gasto máximo: ${stats['gasto_mayor']:,.2f}
• Gasto mínimo: ${stats['gasto_menor']:,.2f}
"""
        
        st.download_button(
            label="📊 Reporte Resumen",
            data=reporte_resumen,
            file_name=f'reporte_resumen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mime='text/plain',
            help="Descarga un reporte resumido de tus finanzas"
        )

with col4:
    if not df_filtrado.empty and not gastos_recurrentes.empty:
        # Reporte de gastos recurrentes
        reporte_recurrentes = "GASTOS RECURRENTES IDENTIFICADOS\n"
        reporte_recurrentes += "=" * 35 + "\n\n"
        
        for _, gasto in gastos_recurrentes.head(10).iterrows():
            reporte_recurrentes += f"• {gasto['categoria']} - {gasto['nota']}\n"
            reporte_recurrentes += f"  Frecuencia: {gasto['frecuencia']} veces\n"
            reporte_recurrentes += f"  Monto promedio: ${gasto['monto_promedio']:,.2f}\n"
            reporte_recurrentes += f"  Cada {gasto['frecuencia_dias']:.0f} días\n\n"
        
        st.download_button(
            label="🔄 Gastos Recurrentes",
            data=reporte_recurrentes,
            file_name=f'gastos_recurrentes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mime='text/plain',
            help="Descarga el análisis de gastos recurrentes"
        )

# Footer mejorado
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h4>💰 Control Financiero Personal Avanzado</h4>
    <p>Dashboard desarrollado con Streamlit | Modo: {modo_analisis}</p>
    <p>Última actualización: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    <p>Total de registros procesados: {len(df_gastos):,}</p>
</div>
""", unsafe_allow_html=True)
