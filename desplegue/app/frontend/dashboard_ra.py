import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

# --- CONFIGURACION DE LA PAGINA ---
st.set_page_config(
    page_title="Dashboard Regularización Ambiental",
    page_icon="📊",
    layout="wide",
)

# --- CONFIGURACION DE CONEXION ---
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_reg_v1"

@st.cache_resource
def get_engine():
    conn_str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"
    return create_engine(
        conn_str,
        pool_pre_ping=True,
        pool_recycle=3600
    )

def load_data():
    engine = get_engine()
    query = "SELECT * FROM dw.v_dashboard_regularizacion"
    df = pd.read_sql(query, engine)
    return df

# --- TITULO ---
st.title("📊 Dashboard de Regularización Ambiental (RA)")
st.markdown("""
Esta aplicación visualiza las métricas clave extraídas del Data Warehouse.
""")

try:
    # --- CARGA DE DATOS ---
    df = load_data()

    # --- SIDEBAR - FILTROS ---
    st.sidebar.header("Filtros")
    
    # Filtro de Provincia
    provincias = ["Todos"] + sorted(df["provincia"].unique().tolist())
    selected_provincia = st.sidebar.selectbox("Selecciona Provincia", provincias)
    
    # Filtro de Tipo de Permiso
    permisos = ["Todos"] + sorted(df["tipo_permiso_ambiental"].unique().tolist())
    selected_permiso = st.sidebar.selectbox("Tipo de Permiso", permisos)

    # Aplicar filtros
    filtered_df = df.copy()
    if selected_provincia != "Todos":
        filtered_df = filtered_df[filtered_df["provincia"] == selected_provincia]
    if selected_permiso != "Todos":
        filtered_df = filtered_df[filtered_df["tipo_permiso_ambiental"] == selected_permiso]

    # --- METRICAS PRINCIPALES (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_proyectos = len(filtered_df["codigo_proyecto"].unique())
        st.metric("Total Proyectos", f"{total_proyectos:,}")
        
    with col2:
        total_superficie = filtered_df["superficie_proyecto"].sum()
        st.metric("Superficie Total (ha)", f"{total_superficie:,.2f}")
        
    with col3:
        avg_duracion = filtered_df["duracion_proceso_dias"].mean()
        st.metric("Promedio Proceso (días)", f"{avg_duracion:,.1f}" if not pd.isna(avg_duracion) else "N/A")

    with col4:
        resoluciones = filtered_df["es_resolucion"].sum()
        pct_res = (resoluciones / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        st.metric("Tasa de Resolución", f"{pct_res:.1f}%")

    st.divider()

    # --- GRAFICOS ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Distribución por Tipo de Permiso")
        fig_permiso = px.pie(filtered_df, names="tipo_permiso_ambiental", hole=0.4)
        st.plotly_chart(fig_permiso, use_container_width=True)

    with c2:
        st.subheader("Volumen por Provincia")
        prov_counts = filtered_df["provincia"].value_counts().reset_index()
        prov_counts.columns = ["provincia", "conteo"]
        fig_prov = px.bar(prov_counts, x="provincia", y="conteo", color="conteo", color_continuous_scale="Viridis")
        st.plotly_chart(fig_prov, use_container_width=True)

    st.subheader("Tendencia de Registros")
    # Asegurar que fecha_registro sea datetime
    filtered_df["fecha_registro"] = pd.to_datetime(filtered_df["fecha_registro"])
    trend_df = filtered_df.groupby(filtered_df["fecha_registro"].dt.to_period("M")).size().reset_index(name="Registros")
    trend_df["fecha_registro"] = trend_df["fecha_registro"].astype(str)
    fig_trend = px.line(trend_df, x="fecha_registro", y="Registros", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- TABLA DE DETALLES ---
    if st.checkbox("Mostrar tabla de datos"):
        st.subheader("Detalle de Proyectos")
        st.dataframe(filtered_df[["codigo_proyecto", "nombre_proyecto", "provincia", "tipo_permiso_ambiental", "estado_proyecto"]])

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.info("Asegúrate de que PostgreSQL esté corriendo y las credenciales en el script sean correctas.")
    st.code("""
# Credenciales actuales en el script:
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_reg_v1"
    """)
