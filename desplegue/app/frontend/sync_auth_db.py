from sqlalchemy import create_engine, text
import bcrypt

DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

def hash_p(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with engine.connect() as conn:
    # 1. Asegurar Roles
    conn.execute(text("INSERT INTO dw.roles (role_id, role_name) VALUES (1, 'Admin'), (2, 'User') ON CONFLICT (role_id) DO NOTHING"))
    
    # 2. Asegurar Usuarios
    users = [
        ("admin", "admin123", "Administrador Senior", 1),
        ("usuario", "user123", "Analista de Datos", 2)
    ]
    for u, p, name, rid in users:
        hp = hash_p(p)
        conn.execute(text("""
            INSERT INTO dw.users (username, password_hash, full_name, role_id, status)
            VALUES (:u, :p, :n, :r, 'Active')
            ON CONFLICT (username) DO UPDATE SET password_hash = :p, status = 'Active', role_id = :r
        """), {"u": u, "p": hp, "n": name, "r": rid})
    
    conn.commit()
    print("Base de datos de seguridad sincronizada (Roles y Usuarios).")
