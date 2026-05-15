
import pandas as pd
import psycopg2
import re

def normalize_text(text):
    if not text: return ""
    text = text.upper()
    # Remove accents
    text = re.sub(r'[ÁÀÄÂ]', 'A', text)
    text = re.sub(r'[ÉÈËÊ]', 'E', text)
    text = re.sub(r'[ÍÌÏÎ]', 'I', text)
    text = re.sub(r'[ÓÒÖÔ]', 'O', text)
    text = re.sub(r'[ÚÙÜÛ]', 'U', text)
    text = re.sub(r'[Ñ]', 'N', text)
    # Remove extra spaces
    text = " ".join(text.split())
    return text

def suggest_geography():
    try:
        # Load references
        provinces = pd.read_csv("f:/Datawrehouse_RA/ref_provinces.csv")
        cantons = pd.read_csv("f:/Datawrehouse_RA/ref_cantons.csv")
        
        provinces['norm'] = provinces['province'].apply(normalize_text)
        cantons['norm'] = cantons['canton'].apply(normalize_text)
        
        # Load N/A areas
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        query = """
            SELECT s.area_id, s.area_name, s.area_campus, s.zone_id
            FROM stg.suia_areas_bi s
            JOIN dw.dim_area da ON s.area_id = da.id_area
            WHERE da.provincia = 'N/A' AND da.sk_area > 0;
        """
        df_na = pd.read_sql(query, conn)
        
        # Expert Manual Fixes for common patterns not caught by keyword
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
            "LOJA": ("LOJA", "LOJA")
        }

        results = []
        for _, area in df_na.iterrows():
            name = normalize_text(area['area_name'])
            campus = normalize_text(str(area['area_campus']))
            fullname = f"{name} {campus}"
            
            matched_prov = "N/A"
            matched_cant = "N/A"
            match_type = "None"
            
            # 1. Match Direct Province in Name
            for _, p in provinces.iterrows():
                if p['norm'] in fullname:
                    matched_prov = p['province']
                    match_type = "Province Keyword"
                    break
            
            # 2. Match Canton (and get its province)
            if matched_prov == "N/A":
                for _, c in cantons.iterrows():
                    # Exact word match for Canton to avoid substrings like 'SAL' for 'SALITRE'
                    if re.search(r'\b' + re.escape(c['norm']) + r'\b', fullname):
                        matched_cant = c['canton']
                        matched_prov = c['province']
                        match_type = "Canton Keyword"
                        break
            
            # 3. Expert Manual Patterns (Specific common keywords)
            if matched_prov == "N/A":
                for key, val in expert_manual.items():
                    if key in fullname:
                        matched_prov, matched_cant = val
                        match_type = "Expert Manual Match"
                        break

            # 4. Special Case: Zonal Mapping && Central Directorates
            if matched_prov == "N/A":
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
                        match_type = "Zonal Sede (Expert)"
                elif "DIRECCION DE REGULARIZACION" in name or "PLANIFICACION" in name or "FINANCIERO" in name:
                    # Central Directorates are in Quito
                    matched_prov = "PICHINCHA"
                    matched_cant = "QUITO"
                    match_type = "Central Directorate (Expert)"

            results.append({
                'id_area': area['area_id'],
                'name': area['area_name'],
                'prov_sug': matched_prov,
                'cant_sug': matched_cant,
                'type': match_type
            })

        df_results = pd.DataFrame(results)
        print(f"Total resolved: {len(df_results[df_results['prov_sug'] != 'N/A'])} / {len(df_results)}")
        print("\n--- RESOLVED SAMPLES ---")
        print(df_results.sort_values('type').to_string())
        
        df_results.to_csv("f:/Datawrehouse_RA/proposed_geo_fix_v1_4.csv", index=False)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    suggest_geography()
