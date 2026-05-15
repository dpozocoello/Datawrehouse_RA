import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\auth_utils.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_css_rules = """        /* Unificar el Frame del Formulario de Streamlit */
        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25) !important;
            padding: 2.5rem !important;
            border: none !important;
        }"""

new_css_rules = """        /* Unificar el Frame del Formulario de Streamlit */
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
        
        /* Subtítulo gris sutil */
        .subtitle-text {
            color: #7F8C8D !important;
        }
        """

if old_css_rules in content:
    content = content.replace(old_css_rules, new_css_rules)
    print("SUCCESS: Auth CSS rules updated.")
else:
    print("FAILED TO UPDATE CSS RULES")

old_html_block = """            <div style="text-align: center; margin-bottom: 25px;">
                <img src="{logo_b64}" width="150" style="margin-bottom: 0px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
                <br>
                <img src="{gov_b64}" width="180" style="margin-bottom: 10px;">
                <h2 style="color: #0A3D62; font-family: 'Montserrat', sans-serif; font-weight: 800; margin-bottom: 2px; margin-top:0px; letter-spacing: 0.5px;">ACCESO INSTITUCIONAL</h2>
                <span style="color: #7F8C8D; font-family: 'Open Sans', sans-serif; font-size: 0.95rem; font-weight: 500;">Centro de Inteligencia Ambiental</span>
            </div>"""

new_html_block = """            <div style="text-align: center; margin-bottom: 25px;">
                <img src="{logo_b64}" width="150" style="margin-bottom: 0px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
                <br>
                <img src="{gov_b64}" width="180" style="margin-bottom: 15px;">
                <h2 style="font-family: 'Montserrat', sans-serif; font-weight: 800; margin-bottom: 2px; margin-top:0px; letter-spacing: 0.5px;">ACCESO INSTITUCIONAL</h2>
                <span class="subtitle-text" style="font-family: 'Open Sans', sans-serif; font-size: 0.95rem; font-weight: 600;">Centro de Inteligencia Ambiental</span>
            </div>"""

if old_html_block in content:
    content = content.replace(old_html_block, new_html_block)
    print("SUCCESS: Auth HTML block updated.")
else:
    print("FAILED TO UPDATE HTML BLOCK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
