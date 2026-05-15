
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

def solve_geography_v1_4_final():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # Load references
        provinces_df = pd.read_csv("f:/Datawrehouse_RA/ref_provinces.csv")
        cantons_df = pd.read_csv("f:/Datawrehouse_RA/ref_cantons.csv")
        
        provinces_df['norm'] = provinces_df['province'].apply(normalize_text)
        cantons_df['norm'] = cantons_df['canton'].apply(normalize_text)
        
        # Load N/A areas
        query = """
            SELECT s.area_id, s.area_name, s.area_campus, s.zone_id, s.area_abbreviation
            FROM stg.suia_areas_bi s
            JOIN dw.dim_area da ON s.area_id = da.id_area
            WHERE da.provincia = 'N/A' AND da.sk_area > 0;
        """
        df_na = pd.read_sql(query, conn)
        
        # Expert Manual Fixes (More comprehensive)
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
            "OTQU": ("PICHINCHA", "QUITO"), # Oficina Técnica Quitumbe/Quito
            "CONELEC": ("PICHINCHA", "QUITO"),
            "DZ 10": ("PICHINCHA", "QUITO"), # Planta Central
            "DIRECCION NACIONAL": ("PICHINCHA", "QUITO"),
            "REGULARIZACION": ("PICHINCHA", "QUITO"),
            "FINANCIERA": ("PICHINCHA", "QUITO"),
            "PLANIFICACION": ("PICHINCHA", "QUITO")
        }

        results = []
        for _, area in df_na.iterrows():
            name = normalize_text(area['area_name'])
            campus = normalize_text(str(area['area_campus']))
            abbr = normalize_text(str(area['area_abbreviation']))
            fullname = f"{name} {campus} {abbr}"
            
            matched_prov = "N/A"
            matched_cant = "N/A"
            
            # 1. Expert Manual Patterns First
            for key, val in expert_manual.items():
                if key in fullname:
                    matched_prov, matched_cant = val
                    break
            
            if matched_prov == "N/A":
                # 2. Match Direct Canton in Name or Campus
                for _, c in cantons_df.iterrows():
                    if re.search(r'\b' + re.escape(c['norm']) + r'\b', fullname):
                        matched_cant = c['canton']
                        matched_prov = c['province']
                        break
            
            if matched_prov == "N/A":
                # 3. Match Direct Province in Name or Campus
                for _, p in provinces_df.iterrows():
                    if p['norm'] in fullname:
                        matched_prov = p['province']
                        matched_cant = p['province']
                        break
            
            if matched_prov == "N/A":
                # 4. Special Case: Zonal Mapping / Central Sede
                if any(x in fullname for x in ["ZONAL", "ZONA", "DZ"]):
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
                    if z and z in zonal_map:
                        matched_prov, matched_cant = zonal_map[z]
                    else:
                        # Fallback for DZ entries without zone_id in record (e.g. Zonal 4 in name)
                        if "4" in fullname: matched_prov, matched_cant = ('MANABI', 'PORTOVIEJO')
                        elif "8" in fullname: matched_prov, matched_cant = ('GUAYAS', 'GUAYAQUIL')
                        elif "9" in fullname: matched_prov, matched_cant = ('PICHINCHA', 'QUITO')
                        
                elif any(x in fullname for x in ["DIRECCION", "PLANIFICACION", "UNIDAD", "SUBSECRETARIA", "COORDINACION"]):
                    matched_prov = "PICHINCHA"
                    matched_cant = "QUITO"

            results.append({
                'id_area': area['area_id'],
                'name': area['area_name'],
                'prov_sug': matched_prov,
                'cant_sug': matched_cant
            })

        df_results = pd.DataFrame(results)
        df_results.to_csv("f:/Datawrehouse_RA/proposed_geo_fix_v1_4.csv", index=False)
        print(f"Total resolved: {len(df_results[df_results['prov_sug'] != 'N/A'])} / {len(df_results)}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_geography_v1_4_final()
