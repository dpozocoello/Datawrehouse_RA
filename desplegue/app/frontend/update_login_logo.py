import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\auth_utils.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_logo_load = """def login_screen():
    # Logo institutional
    logo_path = 'd:/DashboardRA/assets/eco_sieaa/logo_main.png'
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Fondo Navy Oscuro con Blur"""

new_logo_load = """def login_screen():
    # Logo institutional
    logo_path = 'd:/DashboardRA/assets/eco_sieaa/logo_main.png'
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Logo gubernamental
    gov_path = 'd:/DashboardRA/assets/branding/ministerio.png'
    gov_b64 = ""
    if os.path.exists(gov_path):
        with open(gov_path, "rb") as f:
            gov_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    # Fondo Navy Oscuro con Blur"""

old_html_block = """<img src="{logo_b64}" width="160" style="margin-bottom: 20px;">
                <h1 style="color: #0A3D62 !important; font-family: 'Montserrat', sans-serif; font-weight: 700; margin-bottom: 5px;">BIENVENIDO</h1>"""

new_html_block = """<img src="{logo_b64}" width="160" style="margin-bottom: 5px;">
                <p style="margin-bottom: 15px;"><img src="{gov_b64}" width="180"></p>
                <h1 style="color: #0A3D62 !important; font-family: 'Montserrat', sans-serif; font-weight: 700; margin-bottom: 5px;">BIENVENIDO</h1>"""

if old_logo_load in content and old_html_block in content:
    content = content.replace(old_logo_load, new_logo_load)
    content = content.replace(old_html_block, new_html_block)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("FAILED TO FIND TARGET BLOCKS")
    print("old_logo_load found:", old_logo_load in content)
    print("old_html_block found:", old_html_block in content)
