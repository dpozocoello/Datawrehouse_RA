import os
import shutil

def create_desplegue():
    base_dir = "d:/Datawrehouse_RA"
    dist_dir = os.path.join(base_dir, "desplegue")
    db_dir = os.path.join(dist_dir, "db")
    install_dir = os.path.join(dist_dir, "install")
    backend_dist = os.path.join(dist_dir, "app", "backend")
    frontend_dist = os.path.join(dist_dir, "app", "frontend")

    # 1. Limpieza y creación de directorios
    print("--- Iniciando creación de carpeta de DESPLEGUE ---")
    
    if os.path.exists(dist_dir):
        print("Limpiando versión anterior de 'desplegue'...")
        # En Windows, usamos PowerShell para manejar rutas largas y forzar eliminación
        import subprocess
        try:
            cmd = f'powershell -Command "Remove-Item -Path \'{dist_dir}\' -Recurse -Force -ErrorAction SilentlyContinue"'
            subprocess.run(cmd, shell=True, check=False)
            
            # Verificación y fallback con shutil si falla o quedan restos
            if os.path.exists(dist_dir):
                def remove_readonly(func, path, excinfo):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(dist_dir, onerror=remove_readonly)
        except Exception as e:
            print(f"Nota: La limpieza automática tuvo advertencias: {e}")
            print("Si el script falla, borre la carpeta 'desplegue' manualmente.")
    
    for d in [db_dir, install_dir, backend_dist, frontend_dist]:
        os.makedirs(d, exist_ok=True)

    # 2. Consolidación de Base de Datos
    print("Consolidando base de datos (DDL + Catálogos)...")
    ddl_file = os.path.join(base_dir, "ddl_dwh_completo_v1_9_5.sql")
    ref_file = os.path.join(base_dir, "setup_reference_data_v1_4.sql")
    output_db = os.path.join(db_dir, "01_install_db.sql")

    with open(output_db, "w", encoding="utf-8") as outfile:
        if os.path.exists(ddl_file):
            with open(ddl_file, "r", encoding="utf-8") as infile:
                outfile.write("-- =========================================\n")
                outfile.write("-- 1. ESTRUCTURA DDL\n")
                outfile.write("-- =========================================\n")
                outfile.write(infile.read())
                outfile.write("\n\n")
        
        if os.path.exists(ref_file):
            with open(ref_file, "r", encoding="utf-8") as infile:
                outfile.write("-- =========================================\n")
                outfile.write("-- 2. DATOS DE REFERENCIA Y CATALOGOS\n")
                outfile.write("-- =========================================\n")
                outfile.write(infile.read())
    
    # 3. Copia de Catalogs CSV
    print("Copiando catálogos CSV...")
    for csv_file in ["ref_cantons.csv", "ref_provinces.csv", "coa_mae_tables.csv"]:
        src_csv = os.path.join(base_dir, csv_file)
        if os.path.exists(src_csv):
            shutil.copy2(src_csv, db_dir)

    # 4. Copia de Aplicaciones con exclusiones
    def copy_with_ignore(src, dst, ignore_list):
        if os.path.exists(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_list), dirs_exist_ok=True)

    backend_ignore = [
        ".git", ".venv", ".venv_old", "backups", "log", "logs", 
        "desplegue", "__pycache__", "*.pyc", "*.log", "*.tmp",
        "pdi-ce-11.0.0.0-237.zip", ".claude", "documentación", "documentación1", 
        "Documentacion_Entregables_v1_v2_v3"
    ]
    
    frontend_ignore = [
        ".git", ".venv", "BACKUP_*", ".pytest_cache", "__pycache__", 
        "*.pyc", ".vscode", "Puerto", ".claude"
    ]

    print("Empaquetando Backend...")
    copy_with_ignore(base_dir, backend_dist, backend_ignore)
    
    print("Empaquetando Frontend...")
    copy_with_ignore("d:/DashboardRA", frontend_dist, frontend_ignore)

    print(f"\n--- Carpeta '{dist_dir}' generada exitosamente ---")

if __name__ == "__main__":
    create_desplegue()
