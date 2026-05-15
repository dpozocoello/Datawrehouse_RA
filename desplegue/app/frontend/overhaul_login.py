import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\auth_utils.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """    # Fondo Navy Oscuro con Blur
    st.markdown(\"\"\"
    <style>
        .stApp {
            background: linear-gradient(135deg, #0A3D62 0%, #154360 100%) !important;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 450px;
            margin: auto;
        }
    </style>
    \"\"\", unsafe_allow_html=True)

    # Centrado vertical usando columnas
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    _, col_main, _ = st.columns([1, 2, 1])
    
    with col_main:
        with st.container():
            st.markdown(f'''
            <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); text-align: center;">
                <img src="{logo_b64}" width="160" style="margin-bottom: 5px;">
                <p style="margin-bottom: 15px;"><img src="{gov_b64}" width="180"></p>
                <h1 style="color: #0A3D62 !important; font-family: 'Montserrat', sans-serif; font-weight: 700; margin-bottom: 5px;">BIENVENIDO</h1>
                <p style="color: #64748B !important; font-family: 'Open Sans', sans-serif; margin-bottom: 30px;">Centro de Inteligencia ECO-SIEAA</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Formulario nativo fuera del HTML pero visualmente dentro debido al contenedor
            with st.form("login_form_st"):
                user = st.text_input("Usuario", placeholder="nombre.usuario")
                pwd = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("ACCEDER AL CENTRO", use_container_width=True)"""

new_block = """    # UI/UX Overhaul: Single Cohesive Glassmorphism Card
    st.markdown(\"\"\"
    <style>
        .stApp {
            background: radial-gradient(circle at center, #154360 0%, #0A3D62 100%) !important;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Unificar el Frame del Formulario de Streamlit */
        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25) !important;
            padding: 2.5rem !important;
            border: none !important;
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
    \"\"\", unsafe_allow_html=True)

    # Centrado vertical optimizado usando columnas
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    _, col_main, _ = st.columns([1, 1.3, 1])
    
    with col_main:
        # Formulario unificado 
        with st.form("login_form_st", clear_on_submit=False):
            # Renderizado Gráfico dentro de los bordes del st.form
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="{logo_b64}" width="150" style="margin-bottom: 0px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
                <br>
                <img src="{gov_b64}" width="180" style="margin-bottom: 10px;">
                <h2 style="color: #0A3D62; font-family: 'Montserrat', sans-serif; font-weight: 800; margin-bottom: 2px; margin-top:0px; letter-spacing: 0.5px;">ACCESO INSTITUCIONAL</h2>
                <span style="color: #7F8C8D; font-family: 'Open Sans', sans-serif; font-size: 0.95rem; font-weight: 500;">Centro de Inteligencia Ambiental</span>
            </div>
            ''', unsafe_allow_html=True)
            
            user = st.text_input("Usuario Institucional", placeholder="nombre.apellido")
            pwd = st.text_input("Clave de Seguridad", type="password", placeholder="••••••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("AUTENTICAR SESIÓN", use_container_width=True)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("SUCCESS")
else:
    print("FAILED")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
