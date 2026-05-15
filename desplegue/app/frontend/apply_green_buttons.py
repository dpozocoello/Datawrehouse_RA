import os

auth_path = r'd:\\DashboardRA\\Dash_board_RG_v1.01\\auth_utils.py'
config_path = r'd:\\DashboardRA\\Dash_board_RG_v1.01\\config_utils.py'

# 1. Update Auth Utils (Login Screen Button)
with open(auth_path, 'r', encoding='utf-8') as f:
    auth_content = f.read()

old_auth_css = """        /* Protección Estratégica: El texto del botón debe ser Blanco Absoluto */
        [data-testid="stFormSubmitButton"] p, [data-testid="stFormSubmitButton"] span {
            color: #FFFFFF !important;"""

new_auth_css = """        /* Protección Estratégica: El texto del botón debe ser Verde Institucional */
        [data-testid="stFormSubmitButton"] p, [data-testid="stFormSubmitButton"] span {
            color: #2ECC71 !important;"""

if old_auth_css in auth_content:
    auth_content = auth_content.replace(old_auth_css, new_auth_css)
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(auth_content)
    print("SUCCESS: Auth Button Typography shifted to Green.")
else:
    print("FAILED TO UPDATE AUTH BUTTON CSS")

# 2. Update Config Utils (Main Dashboard Buttons)
with open(config_path, 'r', encoding='utf-8') as f:
    config_content = f.read()

old_config_css1 = """        /* Primario y por Defecto: Navy Gradient con Texto Blanco */
        div.stButton > button {
            background: linear-gradient(90deg, #0A3D62 0%, #154360 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }"""
        
new_config_css1 = """        /* Primario y por Defecto: Navy Gradient con Texto Verde */
        div.stButton > button {
            background: linear-gradient(90deg, #0A3D62 0%, #154360 100%) !important;
            color: #2ECC71 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }"""

old_config_css2 = """        /* Secundario explícito (Botones Blancos de Streamlit) */
        div.stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] {
            background: #FFFFFF !important;
            color: #0A3D62 !important;
            border: 1px solid #0A3D62 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }"""
        
new_config_css2 = """        /* Secundario explícito (Botones Blancos de Streamlit) */
        div.stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] {
            background: #FFFFFF !important;
            color: #2ECC71 !important;
            border: 1px solid #2ECC71 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }"""

# Ensure we replace both in config
if old_config_css1 in config_content:
    config_content = config_content.replace(old_config_css1, new_config_css1)
if old_config_css2 in config_content:
    config_content = config_content.replace(old_config_css2, new_config_css2)
    
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)
print("SUCCESS: Config Dashboard Buttons shifted to Green.")
