import os
from PIL import Image

# 1. Hacer el Logo ECO-SIEAA Transparente
src_logo = 'd:/DashboardRA/assets/eco_sieaa/logo_main.png'
dest_logo = 'd:/DashboardRA/assets/eco_sieaa/logo_main_trans.png'

try:
    img = Image.open(src_logo)
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    # Strip white background 
    for item in datas:
        # If RGB values are highly white
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0)) # transparent pixel
        else:
            newData.append(item)
            
    img.putdata(newData)
    img.save(dest_logo, "PNG")
    print("SUCCESS: Logo rendered transparent.")
except Exception as e:
    print(f"FAILED TO CONVERT LOGO: {e}")

# 2. Reemplazar rutas a logo_main_trans.png en auth_utils.py
auth_path = r'd:\DashboardRA\Dash_board_RG_v1.01\auth_utils.py'
with open(auth_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "logo_main.png" in content:
    content = content.replace("logo_main.png", "logo_main_trans.png")
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: auth_utils updated.")

# 3. Reemplazar rutas a logo_main_trans.png en Dash_board_RG_v1.01.py
dash_path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(dash_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "logo_main.png" in content:
    content = content.replace("logo_main.png", "logo_main_trans.png")
    with open(dash_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: dashboard app updated.")

# 4. Eliminar fondo blanco global en config_utils.py
config_path = r'd:\DashboardRA\Dash_board_RG_v1.01\config_utils.py'
with open(config_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_css = """        /* CONTENEDOR PRINCIPAL (#F4F6F7) - AGGRESSIVE OVERRIDE */
        .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stMain"] > div:first-child {
            background-color: #F4F6F7 !important;
            border-radius: 20px 0 0 0;
            padding: 2rem !important;
        }
        .main .block-container {
             background-color: #F4F6F7 !important;
        }"""

new_css = """        /* CONTENEDOR PRINCIPAL TOTALMENTE TRANSPARENTE GLOBAL */
        .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stMain"] > div:first-child, .main .block-container, [data-testid="block-container"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }"""

if old_css in content:
    content = content.replace(old_css, new_css)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Global White Background Strip Finished.")
else:
    print("FAILED TO FIND CSS IN CONFIG")

# Fix Text Colors logically for dark background everywhere 
# Re-open config_path to replace text colors for Dark Mode
with open(config_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# We want white text mostly if the background is Navy
old_text_css = """        html, body, [class*="css"] {
            font-family: 'Open Sans', sans-serif !important;
            font-size: 14px;
            color: #2C3E50; /* Texto sobre fondo claro */
        }"""

new_text_css = """        html, body, [class*="css"] {
            font-family: 'Open Sans', sans-serif !important;
            font-size: 14px;
            color: #FFFFFF !important; /* Texto sobre fondo oscuro naval */
        }
        /* Forzar titulos secundarios a blanco si el nav es oscuro */
        p, span, div, label { color: #ECF0F1 !important; }
        .stMarkdown h3 { color: #27AE60 !important; }"""

if old_text_css in content:
    content = content.replace(old_text_css, new_text_css)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Main Typography shifted to White/Light for Dark bg.")
