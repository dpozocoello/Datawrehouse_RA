import psycopg2
import json
import os

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "utf8"
}

def fix_geography_hierarchy():
    print("Corrección: Sincronizando jerarquía geográfica desde DWH...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Obtener toda la jerarquía de la dimensión corregida
        sql = """
            SELECT sk_geografia, provincia, canton, parroquia
            FROM dw.dim_geografia
            WHERE sk_geografia > 0
            ORDER BY provincia, canton, parroquia
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        hierarchy = []
        for r in rows:
            hierarchy.append({
                "sk": r[0],
                "province": r[1],
                "canton": r[2],
                "parish": r[3]
            })
            
        cur.close()
        conn.close()
        
        output_path = "d:\\Datawrehouse_RA\\area_geo_hierarchy_FIXED.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchy, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Jerarquía geográfica actualizada en: {output_path}")
        print(f"Total registros exportados: {len(hierarchy)} (anteriormente 1009)")
        
    except Exception as e:
        print(f"Error en corrección de geografía: {e}")

if __name__ == "__main__":
    fix_geography_hierarchy()
