import bcrypt
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

def hash_p(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

users = [
    ("admin", "admin123", "Administrador Senior", 1), # Role 1 = Admin
    ("usuario", "user123", "Analista de Datos", 2)    # Role 2 = Standard
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
