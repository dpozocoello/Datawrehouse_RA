import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Integridad DWH - MAATE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
@st.cache_resource
def get_engine():
    """Retorna una conexión a la base de Datos PostgreSQL."""
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

# --- CARGADORES DE DATOS ---
@st.cache_data(ttl=600)
def load_integrity_summary():
    engine = get_engine()
    query = "SELECT * FROM dw.v_integridad_dashboard"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=600)
def load_error_details():
    engine = get_engine()
    query = "SELECT * FROM public.vw_detalle_errores_carga"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=600)
def load_payment_summary():
    engine = get_engine()
    query = "SELECT origen, SUM(monto_pagado) as total_pagado, COUNT(*) as num_transacciones FROM dw.fact_pago GROUP BY 1"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=600)
def load_payment_details():
    engine = get_engine()
    query = """
    SELECT p.codigo_proyecto, p.nombre_proyecto, f.monto_pagado, f.numero_transaccion, f.origen 
    FROM dw.fact_pago f 
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=600)
def load_overlap_summary():
    engine = get_engine()
    query = "SELECT codigo_proyecto, nombre_proyecto, interseccion_snap, areas_protegidas, provincia, canton FROM dw.v_dashboard_regularizacion WHERE interseccion_snap = 'SI'"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=600)
def load_geographic_analysis():
    engine = get_engine()
    query = "SELECT * FROM public.vw_analisis_geografico_proyectos"
    return pd.read_sql(query, engine)


@st.cache_data(ttl=600)
def load_final_metrics():
    engine = get_engine()
    query = "SELECT * FROM public.vw_resumen_final_dashboard"
    return pd.read_sql(query, engine)

# --- SIDEBAR / NAVEGACIÓN ---
st.sidebar.image("https://www.ambiente.gob.ec/wp-content/uploads/downloads/2021/05/LOGO-MAATE-BLANCO.png", width=200)
st.sidebar.title("Panel de Control")

posicion_menu = st.sidebar.radio("Posición del Menú", ["Lateral (Sidebar)", "Superior (Tabs)"])

menu_options = [
    "🏠 Inicio",
    "🔍 Integridad del DWH",
    "📁 Detalle de Errores",
    "💰 Reporte de Pagos",
    "💳 Reporte Detallado de Pagos",
    "🌍 Superposición Ambiental",
    "�� Análisis Geográfico",
    "📈 Informe Final de Métricas"
]

if posicion_menu == "Lateral (Sidebar)":
    selected_tab = st.sidebar.selectbox("Seleccionar Sección", menu_options)
    tab_index = menu_options.index(selected_tab)
else:
    tabs = st.tabs(menu_options)

# --- TÍTULO PRINCIPAL ---
st.title("��️ Sistema de Monitoreo de Integridad DWH")
st.markdown("---")

# --- TABS 0-5 ---

# Tab 0: Inicio
show_tab0 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 0) or (posicion_menu == "Superior (Tabs)")
if show_tab0:
    with (tabs[0] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.subheader("Bienvenido")
        st.info("Este dashboard permite supervisar la integridad y los indicadores ambientales del DWH.")

# Tab 1: Integridad
show_tab1 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 1) or (posicion_menu == "Superior (Tabs)")
if show_tab1:
    with (tabs[1] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("🔍 Integridad del DWH")
        try:
            df = load_integrity_summary()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# Tab 2: Errores
show_tab2 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 2) or (posicion_menu == "Superior (Tabs)")
if show_tab2:
    with (tabs[2] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("📁 Detalle de Errores")
        try:
            df = load_error_details()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# Tab 3: Pagos
show_tab3 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 3) or (posicion_menu == "Superior (Tabs)")
if show_tab3:
    with (tabs[3] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("💰 Resumen de Pagos")
        try:
            df = load_payment_summary()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# Tab 4: Detalle Pagos
show_tab4 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 4) or (posicion_menu == "Superior (Tabs)")
if show_tab4:
    with (tabs[4] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("💳 Detalle de Pagos por Proyecto")
        try:
            df = load_payment_details()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# Tab 5: Superposición
show_tab5 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 5) or (posicion_menu == "Superior (Tabs)")
if show_tab5:
    with (tabs[5] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("🌍 Superposición Ambiental")
        try:
            df = load_overlap_summary()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# --- TABS 6-8 ---

# Tab 6: Análisis Geográfico
show_tab6 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 6) or (posicion_menu == "Superior (Tabs)")
if show_tab6:
    with (tabs[6] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("📍 Análisis Geográfico de Proyectos")
        try:
            df = load_geographic_analysis()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")

# Tab 7: Métricas Finales
show_tab7 = (posicion_menu == "Lateral (Sidebar)" and tab_index == 7) or (posicion_menu == "Superior (Tabs)")
if show_tab7:
    with (tabs[7] if posicion_menu == "Superior (Tabs)" else st.container()):
        st.header("📈 Informe Final de Métricas")
        try:
            df = load_final_metrics()
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"Error: {e}")
