import os
import shutil

source_img = r"C:\Users\javier.pozo\.gemini\antigravity\brain\6fa9ea5b-28c1-401f-b273-6fd3c280173b\media__1774645128198.png"
target_img = r"d:\DashboardRA\assets\eco_sieaa\bg_login.png"

# 1. Copiar la imagen subida al portafolio de assets del dashboard
shutil.copy2(source_img, target_img)
print(f"COPIED IMAGE TO {target_img}")

# 2. Modificar auth_utils.py para cargar y renderizar la imagen
auth_path = r'd:\DashboardRA\Dash_board_RG_v1.01\auth_utils.py'
with open(auth_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Bloque a reemplazar - Añadiendo lectura del Background Base64
old_logo_block = """    # Logo institucional
    logo_path = 'd:/DashboardRA/assets/eco_sieaa/logo_main_trans.png'
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Logo gubernamental"""

new_logo_block = """    # Logo institucional
    logo_path = 'd:/DashboardRA/assets/eco_sieaa/logo_main_trans.png'
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Wallpaper Background HD
    bg_path = 'd:/DashboardRA/assets/eco_sieaa/bg_login.png'
    bg_b64 = ""
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            bg_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Logo gubernamental"""

# Bloque de CSS a reemplazar
old_css_gradient = """        .stApp {
            background: radial-gradient(circle at center, #154360 0%, #0A3D62 100%) !important;
        }"""
        
new_css_wallpaper = """        .stApp {
            background-image: url('""" + "{bg_b64}" + """') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }"""

if old_logo_block in content and old_css_gradient in content:
    content = content.replace(old_logo_block, new_logo_block)
    # Use f-string injection correctly in python script output:
    content = content.replace(old_css_gradient, f"""        .stApp {{
            background-image: url('{bg_b64}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}""")
    with open(auth_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Inyectada la imagen de fondo en stApp (Login).")
else:
    print("FAILED TO FIND CSS COMPONENT OR LOGO BLOCK")
