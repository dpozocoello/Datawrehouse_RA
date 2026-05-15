import os
import sys

# Configuración de rutas dinámica
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, PROJECT_ROOT

def dump_details():
    try:
        # ... (conexión)
        output_path = os.path.join(PROJECT_ROOT, "etl", "ingesta", "intersection_details.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Auditoría de Intersección SNAP (Proyecto 495449)/n/n")
            f.write(f"**Código de Certificado**: {result[0]}/n/n")
            
            f.write("## 1. Ubicación (cein_location)/n")
            f.write("```html/n" + (result[1] if result[1] else "NONE") + "/n```/n/n")
            
            f.write("## 2. Capas Intersecadas (cein_layers)/n")
            f.write("```html/n" + (result[2] if result[2] else "NONE") + "/n```/n/n")
            
            f.write("## 3. Otras Intersecciones (cein_other_intersection)/n")
            f.write("```html/n" + (result[3] if result[3] else "NONE") + "/n```/n/n")
            
            # 4. Capas Activas
            f.write("## 4. Capas del Sistema (coa_mae.layers)/n")
            cur.execute("SELECT laye_id, laye_status, laye_intersection_certificate FROM coa_mae.layers WHERE laye_status AND laye_intersection_certificate")
            layers = cur.fetchall()
            f.write(f"Total Capas Activas para Intersección: {len(layers)}/n/n")
            
        print("Audit details dumped to d://Datawrehouse_RA//etl//ingesta//intersection_details.md")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    dump_details()
