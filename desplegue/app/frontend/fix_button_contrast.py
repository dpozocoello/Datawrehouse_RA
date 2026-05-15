import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\config_utils.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_button_css = """        /* BOTONES Y ACCIONES (JERARQUÍA LUXURY) */
        .stButton>button {
            border-radius: 8px !important;
            padding: 10px 16px !important;
            transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            border: none !important;
            width: auto;
        }
        /* Primario: Verde Ambiental */
        div.stButton > button[kind="secondaryFormSubmit"], 
        div.stButton > button:not([kind="secondary"]):not([kind="primary"]) {
            background-color: #27AE60 !important;
            color: white !important;
        }
        div.stButton > button:hover {
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3) !important;
            transform: translateY(-1px);
        }

        /* SECUNDARIO - AZUL AGUA */
        /* Para usar en dash, requiere inyectar clase .btn-secondary o similar, 
           pero via Streamlit aplicaremos color a botones específicos si es necesario */"""

new_button_css = """        /* BOTONES Y ACCIONES (JERARQUÍA LUXURY) */
        .stButton>button {
            border-radius: 8px !important;
            padding: 10px 16px !important;
            transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            border: none !important;
            width: auto;
        }
        
        /* Primario y por Defecto: Navy Gradient con Texto Blanco */
        div.stButton > button {
            background: linear-gradient(90deg, #0A3D62 0%, #154360 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        div.stButton > button:hover {
            box-shadow: 0 6px 15px rgba(10, 61, 98, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Secundario explícito (Botones Blancos de Streamlit) */
        div.stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] {
            background: #FFFFFF !important;
            color: #0A3D62 !important;
            border: 1px solid #0A3D62 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background: #F4F6F7 !important;
            border-color: #27AE60 !important;
            color: #27AE60 !important;
        }

        /* INPUTS Y TEXT AREAS: Asegurar texto Oscuro cuando el fondo del input es blanco */
        div[data-baseweb="input"] input, 
        div[data-baseweb="select"] *, 
        div[data-baseweb="textarea"] textarea,
        div[data-testid="stDateInput"] input {
            color: #0A3D62 !important;
            font-weight: 500 !important;
        }
        
        /* Fix the dropdown placeholder text specifically */
        div[data-baseweb="select"] span {
            color: #0A3D62 !important;
        }"""

if old_button_css in content:
    content = content.replace(old_button_css, new_button_css)
    print("SUCCESS: Button and Input Contrast CSS Updated.")
else:
    print("FAILED TO FIND OLD BUTTON CSS")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
