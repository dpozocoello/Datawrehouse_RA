import os
import json
import streamlit as st
import base64

def load_config():
    # Usar ruta relativa para mayor portabilidad (Windows/Linux)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "dashboard_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "dashboard_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def apply_custom_theme(palette_name=None):
    """
    ECO-SIEAA Design System: Government Intelligence Center Standard.
    Compliance: WCAG 2.1 AA (4.5:1 Contrast Ratio)
    """
    st.markdown("""
        <style>
        /* IMPORTACIÓN DE TIPOGRAFÍA */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Open+Sans:wght@400;600&display=swap');
        
        /* JERARQUÍA TIPOGRÁFICA GLOBAL */
        html, body, [class*="css"] {
            font-family: 'Open Sans', sans-serif !important;
            font-size: 14px;
            color: #FFFFFF !important; /* Texto sobre fondo oscuro naval */
        }
        /* Forzar titulos secundarios a blanco si el nav es oscuro */
        p, span, div, label { color: #ECF0F1 !important; }
        .stMarkdown h3 { color: #27AE60 !important; }
        
        h1 { font-family: 'Montserrat', sans-serif !important; font-size: 28px !important; font-weight: 700 !important; color: #2ECC71 !important; margin-bottom: 1.5rem !important; }
        h2 { font-family: 'Montserrat', sans-serif !important; font-size: 22px !important; font-weight: 600 !important; color: #2ECC71 !important; }
        h3 { font-family: 'Montserrat', sans-serif !important; font-size: 18px !important; font-weight: 600 !important; color: #34495E !important; }
        
        /* GLOBAL FRAME CONSISTENCY (#0A3D62) */
        .stApp {
            background-color: #0A3D62;
            background-image: 
                linear-gradient(rgba(10, 61, 98, 0.85), rgba(10, 61, 98, 0.85)),
                url(\"data:image/png;base64," + get_base64_raw(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'eco_sieaa', 'bg_network.png')) + "\");
            background-size: cover;
            background-attachment: fixed;
        }

        /* CONTENEDOR PRINCIPAL (#F4F6F7) */
        
        /* CONTENEDOR PRINCIPAL TOTALMENTE TRANSPARENTE GLOBAL */
        .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stMain"] > div:first-child, .main .block-container, [data-testid="block-container"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }


        /* SIDEBAR PROFESIONAL */
        section[data-testid="stSidebar"] {
            background-color: #0A3D62 !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {
            padding: 2rem 1rem !important;
        }
        /* Active nav item highlight - UX PREMIUM: VISIBILIDAD DE SELECCIÓN MEJORADA */
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
            background-color: transparent !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 1px solid transparent !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {
            background-color: rgba(255,255,255,0.08) !important;
            transform: translateX(5px);
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
            background: linear-gradient(90deg, rgba(46, 204, 113, 0.15) 0%, rgba(10, 61, 98, 0.0) 100%) !important;
            border-left: 5px solid #2ECC71 !important;
            border-top: 1px solid rgba(46, 204, 113, 0.2) !important;
            border-bottom: 1px solid rgba(46, 204, 113, 0.2) !important;
            box-shadow: -10px 0 20px rgba(46, 204, 113, 0.1) !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] [data-testid="stWidgetLabel"] p {
            color: rgba(255, 255, 255, 0.7) !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] [data-testid="stWidgetLabel"] p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            text-shadow: 0 0 10px rgba(46, 204, 113, 0.3) !important;
        }
        
        /* BOTONES Y ACCIONES (JERARQUÍA LUXURY) */
        .stButton>button {
            border-radius: 8px !important;
            padding: 10px 16px !important;
            transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            border: none !important;
            width: auto;
        }
        
        /* Primario y por Defecto: Navy Gradient con Texto Verde */
        div.stButton > button {
            background: linear-gradient(90deg, #0A3D62 0%, #154360 100%) !important;
            color: #2ECC71 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        div.stButton > button:hover {
            box-shadow: 0 6px 15px rgba(10, 61, 98, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Secundario explícito (Botones de Acción Interna como 'Ver Trámites') */
        div.stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] {
            background: #2ECC71 !important;
            color: #0A3D62 !important;
            border: none !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
            font-weight: 800 !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background: #27AE60 !important;
            color: #0A3D62 !important;
            box-shadow: 0 6px 15px rgba(39, 174, 96, 0.4) !important;
            transform: translateY(-2px);
        }

        /* INPUTS Y TEXT AREAS: Asegurar texto Oscuro cuando el fondo del input es blanco */
        div[data-baseweb="input"] input, 
        div[data-baseweb="textarea"] textarea,
        div[data-testid="stDateInput"] input {
            color: #0A3D62 !important;
            font-weight: 500 !important;
        }
        
        /* MENÚS DESPLEGABLES (Selectbox) - Texto Negro Obligatorio */
        div[data-baseweb="select"] *, 
        div[data-baseweb="popover"] *, 
        ul[data-baseweb="menu"] *,
        li[role="option"] * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* TABLAS ANALÍTICAS */
        .stDataFrame {
            font-family: 'Open Sans', sans-serif !important;
            font-size: 13px !important;
        }
        .stDataFrame [data-testid="stTable"] thead tr th {
            background-color: #0A3D62 !important;
            color: white !important;
            font-family: 'Montserrat', sans-serif !important;
            text-transform: uppercase;
            font-size: 12px;
            padding: 12px !important;
        }
        .stDataFrame table tr:nth-child(even) { background-color: #F4F6F7 !important; }
        .stDataFrame table tr:hover { background-color: #E8F6F3 !important; }

        /* TARJETAS KPI (ESTILO NASA) */
        .kpi-card {
            background: white !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            text-align: center !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
            border: 1px solid #E5E7E9 !important;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .kpi-card:hover { transform: scale(1.02); }
        .kpi-value {
            font-family: 'Montserrat', sans-serif !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: #0A3D62 !important;
            margin: 0.5rem 0;
        }
        .kpi-label {
            color: #64748B !important;
            font-size: 1rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        /* MODAL DE LOGIN (NUCLEAR OVERLAY) */
        .login-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: rgba(10, 61, 98, 0.95);
            backdrop-filter: blur(10px);
            z-index: 1000000;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-card {
            background: white;
            width: 420px;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
        }

        /* IMÁGENES 16:9 Y CENTRADO */
        .stImage > img {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 900px !important;
            margin-left: auto;
            margin-right: auto;
        }

        /* CABECERA (VISIBILIDAD ABSOLUTA) */
        .header-subtitle { color: #FFFFFF !important; opacity: 1 !important; font-weight: 400 !important; }
        .header-analyst { color: #2ECC71 !important; opacity: 1 !important; font-weight: 600 !important; }

        /* --- UX EXPANDERS (MENÚS DESPLEGABLES DE INFORMACIÓN) --- */
        [data-testid="stExpander"] {
            background-color: transparent !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            margin-bottom: 1rem !important;
            transition: all 0.3s ease !important;
            overflow: hidden !important;
        }
        
        /* Header Inactivo */
        [data-testid="stExpander"] summary {
            background-color: rgba(255, 255, 255, 0.03) !important;
            padding: 0.5rem 1rem !important;
            color: #FFFFFF !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stExpander"] summary:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
        }
        [data-testid="stExpander"] summary p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* ESTADO ACTIVO (SELECCIONADO/ABIERTO) */
        [data-testid="stExpander"][details][open] {
            border: 1px solid rgba(46, 204, 113, 0.4) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
            background-color: rgba(10, 61, 98, 0.4) !important;
        }
        
        [data-testid="stExpander"][details][open] summary {
            background-color: rgba(46, 204, 113, 0.2) !important; /* Verde Esmeralda Transparente para indicar Selección */
            border-bottom: 1px solid rgba(46, 204, 113, 0.3) !important;
        }
        
        [data-testid="stExpander"][details][open] summary p {
            color: #2ECC71 !important; /* Texto Verde cuando está abierto */
            font-weight: 800 !important;
        }
        
        [data-testid="stExpander"] div[role="region"] {
            background-color: transparent !important;
            padding: 1.5rem !important;
        }
    """, unsafe_allow_html=True)

def apply_global_frame():
    """Marco ECO-SIEAA Minimalista"""
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 92% !important;
    }
    footer {display:none !important;}
    </style>
    """, unsafe_allow_html=True)

def get_base64_raw(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def get_base64_image(file_path):
    encoded = get_base64_raw(file_path)
    if not encoded: return ""
    ext = os.path.splitext(file_path)[1].lower().replace(".", "")
    mime = f"image/{'png' if ext=='png' else 'jpeg' if ext in ['jpg','jpeg'] else ext}"
    return f"data:{mime};base64,{encoded}"

def save_local_image(uploaded_file):
    # Calcular ruta relativa a la raíz del proyecto
    base_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_root, "assets", "eco_sieaa")
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
