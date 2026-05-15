import bcrypt
import streamlit as st
import json
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import os
import base64

# --- CONFIGURACIÓN DE DB ---
import os
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
engine = create_engine(DB_URL)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_password_strength(password):
    """Política ISO 27001: Mínimo 8 caracteres, números y símbolos."""
    if len(password) < 8: return False, "Mínimo 8 caracteres."
    if not any(c.isdigit() for c in password): return False, "Debe incluir números."
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): return False, "Debe incluir símbolos."
    return True, "Fuerte"

def authenticate(username, password):
    query = """
    SELECT u.*, r.role_name 
    FROM dw.users u 
    JOIN dw.roles r ON u.role_id = r.role_id 
    WHERE u.username = :u
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"u": username}).fetchone()
            if not result: return None, "Usuario no encontrado."

            # Password check
            if check_password(password, result.password_hash):
                # Update last login
                conn.execute(text("UPDATE dw.users SET last_login = :now, failed_attempts = 0 WHERE user_id = :uid"), {"now": datetime.now(), "uid": result.user_id})
                conn.commit()
                return {
                    "user_id": result.user_id,
                    "username": result.username,
                    "full_name": result.full_name,
                    "role": result.role_name,
                    "must_change": result.must_change_password
                }, None
            return None, "Contraseña incorrecta."
    except Exception as e:
        return None, f"Error de BD: {str(e)}"

def login_screen():
    # Logo institutional - Usar rutas relativas
    base_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_root, 'assets', 'eco_sieaa', 'logo_main_trans.png')
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Logo gubernamental
    gov_path = os.path.join(base_root, 'assets', 'branding', 'ministerio.png')
    gov_b64 = ""
    if os.path.exists(gov_path):
        with open(gov_path, "rb") as f:
            gov_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Wallpaper Background HD
    bg_path = os.path.join(base_root, 'assets', 'eco_sieaa', 'bg_login.png')
    bg_b64 = ""
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            bg_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # UI/UX Overhaul: Single Cohesive Glassmorphism Card
    st.markdown("""
    <style>
        .stApp {
            background-image: url('data:image/png;base64,""" + bg_b64 + """') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* OVERRIDE GLOBAL WORKSPACE BG: Hacer el contenedor maestro 100% transparente solo en el Login */
        [data-testid="stMain"] > div:first-child, .main .block-container, [data-testid="block-container"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Unificar el Frame del Formulario de Streamlit */
        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25) !important;
            padding: 2.5rem !important;
            border: none !important;
        }
        
        /* CORRECCIÓN UX: Todo el texto dentro de la tarjeta blanca debe ser oscuro, ignorando el blanco global */
        [data-testid="stForm"] p, [data-testid="stForm"] span, [data-testid="stForm"] label, [data-testid="stForm"] h2 {
            color: #0A3D62 !important;
        }
        
        /* Protección Estratégica: El texto del botón debe ser Verde Institucional */
        [data-testid="stFormSubmitButton"] p, [data-testid="stFormSubmitButton"] span {
            color: #2ECC71 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            letter-spacing: 1.5px !important;
        }
        
        
        /* Boton Principal HD */
        [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(90deg, #0A3D62 0%, #154360 100%) !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.3s ease-in-out !important;
            padding: 10px !important;
            margin-top: 15px !important;
            letter-spacing: 1px;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            box-shadow: 0 5px 15px rgba(10, 61, 98, 0.4) !important;
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)

    # Centrado vertical optimizado usando columnas
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    _, col_main, _ = st.columns([1, 1.3, 1])
    
    with col_main:
        # Formulario unificado 
        with st.form("login_form_st", clear_on_submit=False):
            # Renderizado Gráfico dentro de los bordes del st.form
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="{logo_b64}" width="160" style="margin-bottom: 5px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
                <br>
                <img src="{gov_b64}" width="190" style="margin-bottom: 15px;">
                <h2 style="color: #0A3D62; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 1.5rem; margin-top: 10px; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 0.5px;">Centro de Inteligencia Ambiental</h2>
            </div>
            ''', unsafe_allow_html=True)
            
            user = st.text_input("Usuario Institucional", placeholder="nombre.apellido")
            pwd = st.text_input("Clave de Seguridad", type="password", placeholder="••••••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("AUTENTICAR SESIÓN", use_container_width=True)
            
            if submit:
                user_data, error_msg = authenticate(user, pwd)
                if user_data:
                    st.session_state['authenticated'] = True
                    st.session_state['user_data'] = user_data
                    st.rerun()
                else:
                    st.error(error_msg or "Acceso denegado.")

def log_audit(action, module=None, details=None):
    if 'user_data' not in st.session_state: return
    uid = st.session_state['user_data']['user_id']
    query = "INSERT INTO dw.audit_logs (user_id, action, module, details) VALUES (:uid, :act, :mod, :det)"
    try:
        with engine.connect() as conn:
            conn.execute(text(query), {"uid": uid, "act": action, "mod": module, "det": json.dumps(details) if details else None})
            conn.commit()
    except: pass
