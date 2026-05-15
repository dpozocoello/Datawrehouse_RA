
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

def solve_all_111_areas_final():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # Load references
        provinces_df = pd.read_csv("f:/Datawrehouse_RA/ref_provinces.csv")
        cantons_df = pd.read_csv("f:/Datawrehouse_RA/ref_cantons.csv")
        provinces_df['norm'] = provinces_df['province'].apply(normalize_text)
        cantons_df['norm'] = cantons_df['canton'].apply(normalize_text)
        
        # Load ALL areas with NULL gelo_id
        # Removed area_description which doesn't exist
        query = """
            SELECT area_id, area_name, area_campus, zone_id, area_abbreviation
            FROM stg.suia_areas_bi
            WHERE gelo_id IS NULL;
        """
        df_all = pd.read_sql(query, conn)
        
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
            "OTQU": ("PICHINCHA", "QUITO"),
            "CONELEC": ("PICHINCHA", "QUITO"),
            "DIRECCION NACIONAL": ("PICHINCHA", "QUITO"),
            "REGULARIZACION": ("PICHINCHA", "QUITO"),
            "FINANCIERA": ("PICHINCHA", "QUITO"),
            "PLANIFICACION": ("PICHINCHA", "QUITO")
        }

        results = []
        for _, area in df_all.iterrows():
            name = normalize_text(area['area_name'])
            campus = normalize_text(str(area['area_campus']))
            abbr = normalize_text(str(area['area_abbreviation']))
            fullname = f"{name} {campus} {abbr}"
            
            matched_prov = "N/A"
            matched_cant = "N/A"
            
            # 1. Direct Zone Regex (DZ 1, DZ 2...)
            dz_match = re.search(r'DZ\s*(\d+)', fullname)
            if dz_match:
                z_id = int(dz_match.group(1))
                if z_id in zonal_map:
                    matched_prov, matched_cant = zonal_map[z_id]
            
            # 2. Expert Manual
            if matched_prov == "N/A":
                for key, val in expert_manual.items():
                    if key in fullname:
                        matched_prov, matched_cant = val
                        break
            
            # 3. Match Direct Canton in Name
            if matched_prov == "N/A":
                for _, c in cantons_df.iterrows():
                    if re.search(r'\b' + re.escape(c['norm']) + r'\b', fullname):
                        matched_cant = c['canton']
                        matched_prov = c['province']
                        break
            
            # 4. Fallback Zone ID / Central Sede
            if matched_prov == "N/A":
                z = area['zone_id']
                if z and z in zonal_map:
                    matched_prov, matched_cant = zonal_map[z]
                elif any(x in fullname for x in ["DIRECCION", "UNIDAD", "SUBSECRETARIA", "COORDINACION"]):
                    matched_prov = "PICHINCHA"
                    matched_cant = "QUITO"
                elif area['area_id'] == 1 or "NO DELIMITADAS" in name:
                    matched_prov = "ZONAS NO DELIMITADAS"
                    matched_cant = "ZONAS NO DELIMITADAS"
                else:
                    # Final Absolute Fallback for MAATE offices: Quito if nothing else
                    matched_prov = "PICHINCHA"
                    matched_cant = "QUITO"

            results.append({
                'id_area': area['area_id'],
                'name': area['area_name'],
                'prov_sug': matched_prov,
                'cant_sug': matched_cant
            })

        df_results = pd.DataFrame(results)
        df_results.to_csv("f:/Datawrehouse_RA/full_geo_fix_111.csv", index=False)
        print(f"Total resolved: {len(df_results[df_results['prov_sug'] != 'N/A'])} / {len(df_results)}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_all_111_areas_final()
