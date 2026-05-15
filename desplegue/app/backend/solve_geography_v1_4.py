
import pandas as pd
import psycopg2
import re

def normalize_text(text):
    if not text: return ""
    text = text.upper()
    text = re.sub(r'[ÁÀÄÂ]', 'A', text)
    text = re.sub(r'[ÉÈËÊ]', 'E', text)
    text = re.sub(r'[ÍÌÏÎ]', 'I', text)
    text = re.sub(r'[ÓÒÖÔ]', 'O', text)
    text = re.sub(r'[ÚÙÜÛ]', 'U', text)
    text = re.sub(r'[Ñ]', 'N', text)
    text = " ".join(text.split())
    return text

def solve_geography_v1_4():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # Load references
        provinces_df = pd.read_csv("f:/Datawrehouse_RA/ref_provinces.csv")
        cantons_df = pd.read_csv("f:/Datawrehouse_RA/ref_cantons.csv")
        
        provinces_df['norm'] = provinces_df['province'].apply(normalize_text)
        cantons_df['norm'] = cantons_df['canton'].apply(normalize_text)
        
        # Load N/A areas from DWH join STG
        query = """
            SELECT s.area_id, s.area_name, s.area_campus, s.zone_id
            FROM stg.suia_areas_bi s
            JOIN dw.dim_area da ON s.area_id = da.id_area
            WHERE da.provincia = 'N/A' AND da.sk_area > 0;
        """
        df_na = pd.read_sql(query, conn)
        
        # Expert Manual Fixes (Dictionaries for hard cases)
        expert_manual = {
            "MILAGRO": ("GUAYAS", "MILAGRO"),
            "DAULE": ("GUAYAS", "DAULE"),
            "DURAN": ("GUAYAS", "DURAN"),
            "PLAYAS": ("GUAYAS", "PLAYAS"),
            "QUEVEDO": ("LOS RIOS", "QUEVEDO"),
            "BABAHOYO": ("LOS RIOS", "BABAHOYO"),
            "VENTANAS": ("LOS RIOS", "VENTANAS"),
            "VINCES": ("LOS RIOS", "VINCES"),
            "LIBERTAD": ("SANTA ELENA", "LA LIBERTAD"),
            "SANTA ELENA": ("SANTA ELENA", "SANTA ELENA"),
            "SANTO DOMINGO": ("SANTO DOMINGO DE LOS TSACHILAS", "SANTO DOMINGO"),
            "EL CARMEN": ("MANABI", "EL CARMEN"),
            "LOJA": ("LOJA", "LOJA"),
            "URDANETA": ("AZUAY", "OÑA"), # Assuming Urdaneta Oña
            "PUYO": ("PASTAZA", "PASTAZA"),
            "TENA": ("NAPO", "TENA"),
            "IBARRA": ("IMBABURA", "IBARRA"),
            "RIOBAMBA": ("CHIMBORAZO", "RIOBAMBA"),
            "PORTOVIEJO": ("MANABI", "PORTOVIEJO"),
            "GUAYAQUIL": ("GUAYAS", "GUAYAQUIL"),
            "CUENCA": ("AZUAY", "CUENCA"),
            "QUITO": ("PICHINCHA", "QUITO"),
            "LATACUNGA": ("COTOPAXI", "LATACUNGA"),
            "AMBATO": ("TUNGURAHUA", "AMBATO"),
            "GUARANDA": ("BOLIVAR", "GUARANDA"),
            "BABA": ("LOS RIOS", "BABA")
        }

        results = []
        for _, area in df_na.iterrows():
            name = normalize_text(area['area_name'])
            campus = normalize_text(str(area['area_campus']))
            fullname = f"{name} {campus}"
            
            matched_prov = "N/A"
            matched_cant = "N/A"
            
            # 1. Expert Manual Patterns First
            for key, val in expert_manual.items():
                if key in fullname:
                    matched_prov, matched_cant = val
                    break
            
            if matched_prov == "N/A":
                # 2. Match Direct Canton in Name
                for _, c in cantons_df.iterrows():
                    if re.search(r'\b' + re.escape(c['norm']) + r'\b', fullname):
                        matched_cant = c['canton']
                        matched_prov = c['province']
                        break
            
            if matched_prov == "N/A":
                # 3. Match Direct Province in Name
                for _, p in provinces_df.iterrows():
                    if p['norm'] in fullname:
                        matched_prov = p['province']
                        matched_cant = p['province'] # fallback to same name
                        break
            
            if matched_prov == "N/A":
                # 4. Special Case: Zonal Mapping && Central Directorates
                if "ZONAL" in name or "ZONA" in name:
                    z = area['zone_id']
                    zonal_map = {
                        1: ('IMBABURA', 'IBARRA'),
                        2: ('NAPO', 'TENA'),
                        3: ('CHIMBORAZO', 'RIOBAMBA'),
                        4: ('MANABI', 'PORTOVIEJO'),
                        5: ('GUAYAS', 'GUAYAQUIL'),
                        6: ('AZUAY', 'CUENCA'),
                        7: ('LOJA', 'LOJA'),
                        8: ('GUAYAS', 'GUAYAQUIL'),
                        9: ('PICHINCHA', 'QUITO')
                    }
                    if z in zonal_map:
                        matched_prov, matched_cant = zonal_map[z]
                elif any(x in name for x in ["DIRECCION", "PLANIFICACION", "FINANCIERO", "COORDINACION"]):
                    matched_prov = "PICHINCHA"
                    matched_cant = "QUITO"

            results.append({
                'id_area': area['area_id'],
                'name': area['area_name'],
                'prov': matched_prov,
                'cant': matched_cant
            })

        # Generate SQL
        print("--- PROVINCE SQL ---")
        for r in results:
            print(f"WHEN s.area_id = {r['id_area']} THEN '{r['prov']}' -- {r['name']}")
        
        print("\n--- CANTON SQL ---")
        for r in results:
            print(f"WHEN s.area_id = {r['id_area']} THEN '{r['cant']}'")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_geography_v1_4()
