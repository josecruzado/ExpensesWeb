# 💼 Control Financiero Personal

Una aplicación web interactiva desarrollada con Streamlit para ayudarte a visualizar y gestionar tus gastos personales de forma sencilla. Conéctate a tus datos de Firebase, filtra por categoría y fecha, visualiza gráficos y exporta tus transacciones a Excel.

## ✨ Características

* **Visualización de Gastos:** Obtén un resumen rápido de tus gastos totales, promedio y número de transacciones.

* **Gráficos Interactivos:** Visualiza tus gastos por categoría con gráficos de barras dinámicos.

* **Filtrado Flexible:** Filtra tus transacciones por una o varias categorías y por un rango de fechas específico.

* **Detalle de Transacciones:** Consulta una tabla detallada con todas tus transacciones filtradas.

* **Exportación a Excel:** Descarga tus datos filtrados en formato `.xlsx` para un análisis más profundo.

* **Diseño Responsivo:** Optimizado para una experiencia de usuario fluida tanto en dispositivos móviles como de escritorio.

* **Soporte PWA:** Posibilidad de instalar la aplicación directamente en tu dispositivo como una Aplicación Web Progresiva (PWA) para un acceso rápido.

## 🚀 Cómo Funciona

Esta aplicación está construida con:

* **Streamlit:** Para la creación rápida de la interfaz de usuario interactiva.

* **Pandas:** Para la manipulación y análisis de datos.

* **Plotly Express:** Para la generación de gráficos visualmente atractivos.

* **Requests:** Para obtener los datos de una base de datos Firebase en tiempo real.

Los datos de gastos se obtienen de una base de datos Firebase (específicamente, `https://gastos-d660a-default-rtdb.europe-west1.firebasedatabase.app/gastos_registrados.json`).

## ⚙️ Configuración y Ejecución Local

Para ejecutar esta aplicación en tu máquina local, sigue estos pasos:

1. **Clona este repositorio (o guarda el código):**
   Si tienes el código en un archivo `.py`, simplemente guárdalo (ej. `app.py`).

2. **Instala las dependencias:**
   Asegúrate de tener Python instalado. Luego, instala las librerías necesarias usando pip:
