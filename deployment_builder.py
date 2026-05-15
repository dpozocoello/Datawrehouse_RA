import os
import shutil
import re

# Configuración
SOURCE_ROOT = r"d:\Datawrehouse_RA"
DIST_ROOT = os.path.join(SOURCE_ROOT, "dist", "ubuntu")
PROJECT_NAME = "eco-sieaa"

# Mapeo de Reemplazos (Windows -> Ubuntu)
REPLACEMENTS = [
    (r"D:\\Datawrehouse_RA", f"/opt/{PROJECT_NAME}"),
    (r"D:/Datawrehouse_RA", f"/opt/{PROJECT_NAME}"),
    (r"ETL_p", "etl"),
    (r"5432", "5632"),  # Puerto DWH
    (r"\\", "/"),        # Normalizar slashes para Pentaho
    (r"python ", "python3 "), # Asegurar uso de python3 en Linux
    (r"D:/etl_", f"/opt/{PROJECT_NAME}/dwh/etl_"), # Rutas de SQL Directas
    (r"D:\\etl_", f"/opt/{PROJECT_NAME}/dwh/etl_"), # Rutas de SQL Directas
]

def build_deployment():
    print(f"🚀 Iniciando construcción de despliegue para Ubuntu...")
    
    # 1. Limpiar carpeta dist
    if os.path.exists(DIST_ROOT):
        shutil.rmtree(DIST_ROOT)
    os.makedirs(DIST_ROOT)
    
    # 2. Carpetas a procesar
    folders_to_copy = ["ETL_p", "Jobs", "transformations"]
    
    for folder in folders_to_copy:
        src = os.path.join(SOURCE_ROOT, folder)
        # Renombrar ETL_p a etl en el destino
        dest_folder = "etl" if folder == "ETL_p" else folder
        dest = os.path.join(DIST_ROOT, "etl", dest_folder) if folder == "Jobs" else os.path.join(DIST_ROOT, "etl")
        
        if folder == "Jobs":
             dest = os.path.join(DIST_ROOT, "etl", "Jobs")
             
        print(f"📦 Copiando {folder} -> {dest}...")
        shutil.copytree(src, dest, dirs_exist_ok=True)

    # 3. Archivos sueltos
    files_to_copy = ["ddl_dwh_completo_v1_9_5.sql", "area_geo_hierarchy_FIXED.json"]
    os.makedirs(os.path.join(DIST_ROOT, "dwh"), exist_ok=True)
    
    for filename in files_to_copy:
        shutil.copy2(os.path.join(SOURCE_ROOT, filename), os.path.join(DIST_ROOT, "dwh", filename))

    # 4. Procesamiento de Archivos (Reemplazo de rutas)
    print("🧹 Normalizando rutas en archivos .py, .kjb, .ktr y .sql...")
    
    for root, dirs, files in os.walk(DIST_ROOT):
        for file in files:
            if file.endswith((".py", ".kjb", ".ktr", ".sql", ".sh")):
                file_path = os.path.join(root, file)
                
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                new_content = content
                for pattern, replacement in REPLACEMENTS:
                    new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE if "Datawrehouse" in pattern else 0)
                
                if new_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    # print(f"  ✅ {file} normalizado.")

    print(f"\n✨ Construcción completada en: {DIST_ROOT}")
    print(f"👉 Suba el contenido de la carpeta 'dist/ubuntu' al servidor en /opt/{PROJECT_NAME}/")

if __name__ == "__main__":
    build_deployment()
