import os
import re

ddl_raw_path = r"d:\Datawrehouse_RA\ddl_v1_9_5_raw.sql"
ddl_final_path = r"d:\Datawrehouse_RA\ddl_dwh_completo_v1_9_5.sql"

# 1. Definir Componentes Adicionales
header = """-- ==============================================================================
-- ECO-SIEAA DATA WAREHOUSE: SCRIPT MAESTRO DE INSTALACIÓN (CLEAN INSTALL)
-- Versión: 1.9.5 (Producción - Ubuntu 24.04.3 LTS)
-- Fecha: 2026-04-02
-- Autor: Antigravity (Advanced Agentic Coding)
--
-- DESCRIPCIÓN:
--   Este script realiza la creación completa del ecosistema DWH-REG desde cero.
--   Incluye esquemas, extensiones, tablas, auditoría de logs, vistas y SPs.
-- ==============================================================================

"""

sp_intersection = """
-- ==============================================================================
-- sp_carga_dim_intersection
-- ==============================================================================
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_intersection() RETURNS VOID AS $$
BEGIN
    -- 1. Marcar registros antiguos como is_current = FALSE
    UPDATE dw.dim_intersection di
    SET is_current = FALSE
    FROM stg.stg_intersection stg
    JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
    WHERE di.sk_proyecto = dp.sk_proyecto
      AND di.certificate_code != stg.certificate_code;

    -- 2. Insertar nuevos certificados o actualizar existentes
    INSERT INTO dw.dim_intersection (
        sk_proyecto, certificate_code, certificate_date, 
        html_location, html_layers, dictamen_final, is_current
    )
    SELECT 
        dp.sk_proyecto,
        stg.certificate_code,
        stg.certificate_date,
        stg.html_location,
        stg.html_layers,
        stg.dictamen_final,
        TRUE
    FROM stg.stg_intersection stg
    JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
    ON CONFLICT (sk_proyecto, certificate_code) DO UPDATE SET 
        certificate_date = EXCLUDED.certificate_date,
        html_location = EXCLUDED.html_location,
        html_layers = EXCLUDED.html_layers,
        dictamen_final = EXCLUDED.dictamen_final,
        is_current = TRUE;

    ANALYZE dw.dim_intersection;
END;
$$ LANGUAGE plpgsql;
"""

def clean_ddl():
    print(f"Leyendo base DDL desde {ddl_raw_path}...")
    with open(ddl_raw_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_lines = []
    skip_table = False
    
# 2. Definir Patrones de Exclusión
exclude_patterns = [
    r"_bak\d*",             # Tablas de respaldo con fecha/número
    r"tmp_final_waste",     # Tablas temporales de procesos pasados
    r"tmp_dim_proyecto",    # Tablas temporales de optimización
    r"bak_2026",            # Específico para backups de abril
    r"\\restrict",          # Comandos de restricción de psql
    r"\\unrestrict"         # Comandos de des-restricción redundantes
]

def clean_ddl():
    print(f"Leyendo base DDL desde {ddl_raw_path}...")
    with open(ddl_raw_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_lines = []
    
    # 3. Filtrado Agresivo de Referencias Huérfanas
    for line in lines:
        # Si la línea contiene CUALQUIER patrón de exclusión, la saltamos completamente
        # Esto elimina CREATE TABLE, ALTER TABLE, COMMENT, INDEX, etc.
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in exclude_patterns):
            continue
            
        # Si la línea tiene d:\Datawrehouse o similar (corrupciones previas), la ignoramos
        if "Datawrehouse_RA" in line:
            continue

        clean_lines.append(line)

    # 4. Ensamblar Final
    print(f"Ensamblando versión final v1.9.5 (Deep Clean)...")
    with open(ddl_final_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(clean_lines)
        f.write("\n")
        f.write(sp_intersection)
        
    print("Finalización exitosa: ddl_dwh_completo_v1_9_5.sql")

if __name__ == "__main__":
    clean_ddl()
