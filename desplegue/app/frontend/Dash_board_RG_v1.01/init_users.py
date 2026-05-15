import bcrypt
from sqlalchemy import create_engine, text
import json
import os

# CONFIGURACIÓN
DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

TEMP_PASSWORD = "EcoSieaa2026*"

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def run_init():
    print("--- Iniciando Configuración de Usuarios ECO-SIEAA ---")
    
    with engine.connect() as conn:
        # 1. Ejecutar DDL (Estructura)
        print("Cargando estructura de tablas...")
        with open('setup_security_schema.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            conn.execute(text(sql))
        conn.commit()

        # 2. Insertar Roles base (Sincronizados con dashboard_config.json)
        roles = ["ADMIN", "GERENCIA", "MESA_AYUDA", "DESARROLLADOR", "QA"]
        print(f"Insertando roles: {roles}")
        for r in roles:
            conn.execute(text("INSERT INTO dw.roles (role_name) VALUES (:r) ON CONFLICT (role_name) DO NOTHING"), {"r": r})
        conn.commit()

        # 3. Definir Usuarios base
        users_to_create = [
            {"u": "admin.sieaa", "f": "Administrador Maestro SIEAA", "r": "ADMIN"},
            {"u": "gerencia.mae", "f": "Directivo de Gestión Ambiental", "r": "GERENCIA"},
            {"u": "soporte.sieaa", "f": "Analista de Mesa de Ayuda", "r": "MESA_AYUDA"},
            {"u": "dev.javier", "f": "Desarrollador Senior", "r": "DESARROLLADOR"},
            {"u": "test.qa", "f": "Analista de Calidad", "r": "QA"}
        ]

        hashed_pwd = hash_password(TEMP_PASSWORD)
        print(f"Creando usuarios con hash de seguridad...")

        for user in users_to_create:
            # Obtener ID del rol
            role_id = conn.execute(text("SELECT role_id FROM dw.roles WHERE role_name = :r"), {"r": user['r']}).scalar()
            
            # Insertar usuario
            insert_query = """
            INSERT INTO dw.users (username, full_name, password_hash, role_id, must_change_password)
            VALUES (:u, :f, :h, :rid, TRUE)
            ON CONFLICT (username) DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                role_id = EXCLUDED.role_id,
                must_change_password = TRUE
            """
            conn.execute(text(insert_query), {
                "u": user['u'], 
                "f": user['f'], 
                "h": hashed_pwd, 
                "rid": role_id
            })
            print(f"  > Usuario registrado: {user['u']} [{user['r']}]")
        
        conn.commit()
    
    print("--- Proceso Finalizado con Éxito ---")

if __name__ == "__main__":
    run_init()
