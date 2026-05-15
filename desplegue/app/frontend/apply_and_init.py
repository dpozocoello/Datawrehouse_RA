import bcrypt
from sqlalchemy import create_engine, text
import os

DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

def hash_p(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def run():
    # 1. Aplicar Esquema
    with engine.connect() as conn:
        with open('d:/DashboardRA/schema_security.sql', 'r') as f:
            conn.execute(text(f.read()))
            conn.commit()
    print("Esquema aplicado.")

    # 2. Inicializar Usuarios
    users = [
        ("admin", "admin123", "Administrador Senior", 1),
        ("usuario", "user123", "Analista de Datos", 2)
    ]
    with engine.connect() as conn:
        for u, p, name, rid in users:
            hp = hash_p(p)
            conn.execute(text("""
                INSERT INTO dw.users (username, password_hash, full_name, role_id)
                VALUES (:u, :p, :n, :r)
                ON CONFLICT (username) DO UPDATE SET password_hash = :p
            """), {"u": u, "p": hp, "n": name, "r": rid})
            conn.commit()
    print("Usuarios inicializados: admin/admin123 y usuario/user123")

if __name__ == "__main__":
    run()
