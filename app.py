import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from io import BytesIO

# --- Configuración inicial optimizada para iOS ---
st.set_page_config(
    page_title="Control Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Control Financiero - Aplicación web desarrollada con Streamlit"
    }
)

# --- PWA y optimizaciones iOS profesionales ---
st.markdown("""
<head>
    <!-- PWA Manifest -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- iOS Meta Tags -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Control Financiero">
    <meta name="format-detection" content="telephone=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    
    
    <!-- Theme Color -->
    <meta name="theme-color" content="#2E86AB">
    <meta name="msapplication-TileColor" content="#2E86AB">
</head>

<style>
    /* === BASE Y RESET === */
    * {
        box-sizing: border-box;
        -webkit-tap-highlight-color: transparent;
    }
    
    html, body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.5;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }
    
    /* === SAFE AREA PARA NOTCH === */
    .main {
        padding-top: env(safe-area-inset-top);
        padding-bottom: max(env(safe-area-inset-bottom), 20px);
        padding-left: env(safe-area-inset-left);
        padding-right: env(safe-area-inset-right);
    }
    
    /* === HEADER OPTIMIZADO === */
    .stApp > header {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(46, 134, 171, 0.2);
        padding-top: env(safe-area-inset-top);
    }
    
    /* === TÍTULOS === */
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
        font-weight: 600;
        margin: 0.5rem 0;
        color: #1a202c;
    }
    
    h1 { font-size: clamp(1.5rem, 4vw, 2.5rem); }
    h2 { font-size: clamp(1.25rem, 3vw, 2rem); }
    h3 { font-size: clamp(1.125rem, 2.5vw, 1.5rem); }
    
    /* === BOTONES OPTIMIZADOS PARA TOUCH === */
    .stButton > button {
        width: 100%;
        min-height: 48px;
        font-size: 16px;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 12px;
        border: none;
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
        cursor: pointer;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        user-select: none;
        -webkit-user-select: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(46, 134, 171, 0.3);
    }
    
    .stButton > button:focus {
        outline: none;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3), 0 0 0 3px rgba(46, 134, 171, 0.2);
    }
    
    /* === INPUTS OPTIMIZADOS === */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div,
    .stDateInput > div > div > input {
        font-size: 16px !important;
        min-height: 48px;
        padding: 12px 16px;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        background: white;
        transition: all 0.3s ease;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stMultiSelect > div > div > div:focus-within,
    .stDateInput > div > div > input:focus {
        border-color: #2E86AB;
        outline: none;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    /* === MÉTRICAS OPTIMIZADAS === */
    .stMetric {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        border: 1px solid #f7fafc;
        text-align: center;
    }
    
    .stMetric > div {
        font-size: 14px;
        font-weight: 500;
        color: #718096;
        margin-bottom: 8px;
    }
    
    .stMetric > div > div {
        font-size: 28px;
        font-weight: 700;
        color: #2E86AB;
        margin-top: 4px;
    }
    
    /* === TABS OPTIMIZADAS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f7fafc;
        padding: 4px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        color: #4a5568;
        font-weight: 500;
        padding: 0 16px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #2E86AB;
        box-shadow: 0 2px 8px rgba(46, 134, 171, 0.15);
    }
    
    /* === TABLAS RESPONSIVAS === */
    .stDataFrame {
        font-size: 14px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f7fafc;
    }
    
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .stDataFrame th {
        background: #f7fafc;
        padding: 12px 8px;
        font-weight: 600;
        text-align: left;
        border-bottom: 2px solid #e2e8f0;
        color: #4a5568;
    }
    
    .stDataFrame td {
        padding: 12px 8px;
        border-bottom: 1px solid #f7fafc;
        color: #2d3748;
    }
    
    .stDataFrame tr:hover {
        background: #f7fafc;
    }
    
    /* === GRÁFICOS OPTIMIZADOS === */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 16px;
        border: 1px solid #f7fafc;
    }
    
    /* === ALERTAS Y NOTIFICACIONES === */
    .stAlert {
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        border-left: 4px solid;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .stInfo {
        background: #ebf8ff;
        border-left-color: #3182ce;
        color: #2a69ac;
    }
    
    .stSuccess {
        background: #f0fff4;
        border-left-color: #38a169;
        color: #2f855a;
    }
    
    .stError {
        background: #fed7d7;
        border-left-color: #e53e3e;
        color: #c53030;
    }
    
    .stWarning {
        background: #fefcbf;
        border-left-color: #d69e2e;
        color: #b7791f;
    }
    
    /* === CONTENEDORES Y COLUMNAS === */
    .stContainer {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 16px;
    }
    
    .stColumns {
        gap: 16px;
    }
    
    /* === RESPONSIVE DESIGN === */
    @media (max-width: 768px) {
        .stContainer {
            padding: 0 12px;
        }
        
        .stColumns {
            flex-direction: column;
        }
        
        .stColumn {
            width: 100% !important;
            margin-bottom: 16px;
        }
        
        .stButton > button {
            font-size: 16px;
            padding: 14px 16px;
        }
        
        .stDataFrame {
            font-size: 12px;
        }
        
        .stDataFrame th,
        .stDataFrame td {
            padding: 8px 4px;
        }
        
        .stMetric > div > div {
            font-size: 24px;
        }
    }
    
    /* === MODO OSCURO === */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: #1a202c;
            color: #f7fafc;
        }
        
        .stApp > header {
            background: linear-gradient(135deg, #2c5282 0%, #822727 100%);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #f7fafc;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #2c5282 0%, #822727 100%);
        }
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stMultiSelect > div > div > div,
        .stDateInput > div > div > input {
            background: #2d3748;
            color: #f7fafc;
            border-color: #4a5568;
        }
        
        .stMetric {
            background: #2d3748;
            border-color: #4a5568;
        }
        
        .stMetric > div {
            color: #cbd5e0;
        }
        
        .stMetric > div > div {
            color: #63b3ed;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: #2d3748;
        }
        
        .stTabs [aria-selected="true"] {
            background: #4a5568;
            color: #63b3ed;
        }
        
        .stDataFrame {
            background: #2d3748;
            border-color: #4a5568;
        }
        
        .stDataFrame th {
            background: #4a5568;
            color: #f7fafc;
        }
        
        .stDataFrame td {
            color: #f7fafc;
        }
        
        .stDataFrame tr:hover {
            background: #4a5568;
        }
    }
    
    /* === ANIMACIONES === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* === SCROLLBAR PERSONALIZADA === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f7fafc;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a0aec0;
    }
    
    /* === OCULTAR ELEMENTOS INNECESARIOS === */
    .stDeployButton,
    .stDecoration,
    footer,
    .stException,
    #MainMenu {
        display: none;
    }
    
    /* === LOADING SPINNER === */
    .stSpinner {
        border: 3px solid #f7fafc;
        border-top: 3px solid #2E86AB;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* === OPTIMIZACIONES TOUCH === */
    .stButton > button,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        will-change: transform, box-shadow;
    }
    
    /* === HOVER STATES SOLO PARA DESKTOP === */
    @media (hover: hover) and (pointer: fine) {
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
        }
        
        .stDataFrame tr:hover {
            background: #f7fafc;
        }
    }
</style>

<script>
    // === SERVICE WORKER REGISTRATION ===
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered'))
                .catch(error => console.log('SW registration failed'));
        });
    }
    
    // === PWA INSTALL PROMPT ===
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Crear botón de instalación
        const installButton = document.createElement('button');
        installButton.textContent = 'Instalar App 📱';
        installButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        
        installButton.addEventListener('click', () => {
            installButton.style.display = 'none';
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                deferredPrompt = null;
            });
        });
        
        document.body.appendChild(installButton);
    });
    
    // === OPTIMIZACIONES TOUCH ===
    document.addEventListener('touchstart', function() {}, true);
    
    // === PREVENIR DOBLE TAP ZOOM ===
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // === HAPTIC FEEDBACK ===
    function vibrate(duration = 50) {
        if ('vibrate' in navigator) {
            navigator.vibrate(duration);
        }
    }
    
    // Añadir vibración a botones
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON') {
            vibrate(50);
        }
    });
    
    // === GESTIÓN DE ORIENTACIÓN ===
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
    
    // === PREVENIR PULL-TO-REFRESH ===
    let startY = 0;
    
    document.addEventListener('touchstart', (e) => {
        startY = e.touches[0].clientY;
    }, {passive: true});
    
    document.addEventListener('touchmove', (e) => {
        const currentY = e.touches[0].clientY;
        if (startY < currentY && window.scrollY === 0) {
            e.preventDefault();
        }
    }, {passive: false});
    
    // === OPTIMIZACIÓN DE RENDIMIENTO ===
    document.addEventListener('DOMContentLoaded', () => {
        // Añadir loading lazy a imágenes
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.loading = 'lazy';
        });
        
        // Mejorar accesibilidad
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            if (!button.getAttribute('aria-label')) {
                button.setAttribute('aria-label', button.textContent || 'Button');
            }
        });
    });
</script>
""", unsafe_allow_html=True)

# --- Función para obtener datos ---
@st.cache_data(ttl=300)
def obtener_datos():
    try:
        url = "https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json"
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not datos:
            return pd.DataFrame()
        registros = []
        for key, gasto in datos.items():
            registros.append({
                "Categoría": gasto.get("categoria", "Sin categoría"),
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
st.markdown("<h2 style='color: #2E86AB; margin-bottom: 2rem;'>💼 Control Financiero Personal</h2>", unsafe_allow_html=True)

if df.empty:
    st.info("No hay datos disponibles. Verifica la conexión.")
    st.stop()

# --- Filtros optimizados para móvil ---
st.markdown("### 🔍 Filtros")
col1, col2 = st.columns(2)
with col1:
    categorias = st.multiselect(
        "Categorías", 
        options=df["Categoría"].unique(), 
        default=df["Categoría"].unique(),
        help="Selecciona las categorías a mostrar"
    )
with col2:
    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()
    fecha_rango = st.date_input(
        "Rango de fechas", 
        value=(fecha_min, fecha_max),
        help="Selecciona el período a analizar"
    )

# --- Aplicar filtros ---
if len(fecha_rango) == 2:
    df_filtrado = df[
        (df["Categoría"].isin(categorias)) &
        (df["Fecha"].dt.date >= fecha_rango[0]) &
        (df["Fecha"].dt.date <= fecha_rango[1])
    ]
else:
    df_filtrado = df[df["Categoría"].isin(categorias)]

# --- Tabs para navegación móvil ---
tab1, tab2, tab3 = st.tabs(["📊 Resumen", "📁 Gráficos", "📄 Detalles"])

with tab1:
    st.subheader("📈 Métricas Clave")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Gasto Total", 
            f"${df_filtrado['Monto'].sum():,.2f}",
            help="Total de gastos en el período seleccionado"
        )
    
    with col2:
        st.metric(
            "Promedio", 
            f"${df_filtrado['Monto'].mean():,.2f}",
            help="Promedio de gasto por transacción"
        )
    
    with col3:
        st.metric(
            "Transacciones", 
            len(df_filtrado),
            help="Número total de transacciones"
        )
    
    # Métricas adicionales
    if not df_filtrado.empty:
        st.markdown("---")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric(
                "Gasto Mayor", 
                f"${df_filtrado['Monto'].max():,.2f}",
                help="Transacción de mayor monto"
            )
        
        with col5:
            st.metric(
                "Gasto Menor", 
                f"${df_filtrado['Monto'].min():,.2f}",
                help="Transacción de menor monto"
            )
        
        with col6:
            categoria_top = df_filtrado.groupby("Categoría")["Monto"].sum().idxmax()
            st.metric(
                "Categoría Top", 
                categoria_top,
                help="Categoría con mayor gasto total"
            )

with tab2:
    st.subheader("📊 Análisis Visual")
    
    if not df_filtrado.empty:
        # Gráfico por categoría
        st.markdown("#### Gastos por Categoría")
        gastos_categoria = df_filtrado.groupby("Categoría")["Monto"].sum().sort_values(ascending=False)
        
        fig = px.bar(
            gastos_categoria,
            x=gastos_categoria.index,
            y=gastos_categoria.values,
            labels={"x": "Categoría", "y": "Monto ($)"},
            title="Distribución de Gastos por Categoría",
            color=gastos_categoria.values,
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            showlegend=False,
            title_x=0.5,
            title_font_size=16
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de tendencia temporal
        st.markdown("#### Tendencia Temporal")
        df_temporal = df_filtrado.groupby(df_filtrado["Fecha"].dt.date)["Monto"].sum().reset_index()
        
        fig_temporal = px.line(
            df_temporal,
            x="Fecha",
            y="Monto",
            title="Evolución de Gastos en el Tiempo",
            markers=True
        )
        
        fig_temporal.update_layout(
            height=400,
            title_x=0.5,
            title_font_size=16
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)
        
    else:
        st.info("No hay datos para mostrar gráficos.")

with tab3:
    st.subheader("📄 Detalles de Transacciones")
    
    if not df_filtrado.empty:
        # Configurar la visualización de la tabla
        df_display = df_filtrado.copy()
        df_display["Fecha"] = df_display["Fecha"].dt.strftime("%Y-%m-%d")
        df_display["Monto"] = df_display["Monto"].apply(lambda x: f"${x:,.2f}")
        
        # Ordenar por fecha descendente
        df_display = df_display.sort_values("Fecha", ascending=False)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
                "Fecha": st.column_config.DateColumn("Fecha", width="small"),
                "Monto": st.column_config.TextColumn("Monto", width="small"),
                "Nota": st.column_config.TextColumn("Nota", width="large")
            }
        )
        
        # Resumen rápido
        st.markdown("---")
        st.markdown("#### Resumen Rápido")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Total de registros:** {len(df_filtrado)}")
            st.write(f"**Período:** {df_filtrado['Fecha'].min().strftime('%Y-%m-%d')} al {df_filtrado['Fecha'].max().strftime('%Y-%m-%d')}")
        
        with col2:
            st.write(f"**Monto total:** ${df_filtrado['Monto'].sum():,.2f}")
            st.write(f"**Categorías:** {df_filtrado['Categoría'].nunique()}")
            
    else:
        st.info("No hay transacciones para mostrar.")

# --- Exportar a Excel ---
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gastos')
        
        # Obtener el workbook y worksheet
        workbook = writer.book
        worksheet = writer.sheets['Gastos']
        
        # Formato para headers
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#2E86AB',
            'font_color': 'white',
            'border': 1
        })
        
        # Aplicar formato a headers
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ajustar ancho de columnas
        worksheet.set_column('A:A', 20)  # Categoría
        worksheet.set_column('B:B', 15)  # Fecha
        worksheet.set_column('C:C', 15)  # Monto
        worksheet.set_column('D:D', 30)  # Nota
        
        writer.close()
    return output.getvalue()

# --- Sección de exportación ---
st.markdown("---")
st.markdown("### 📥 Exportar Datos")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📥 Descargar en Excel",
        data=convertir_a_excel(df_filtrado),
        file_name=f"gastos_exportados_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )