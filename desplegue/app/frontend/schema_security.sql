-- Esquema de Seguridad y Auditoría para Dashboard RA
-- Autor: Arquitecto Senior / Data Engineer
-- Fecha: 2026-03-26

-- 1. Roles de Usuario
CREATE TABLE IF NOT EXISTS dw.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO dw.roles (role_name, description) VALUES 
('Admin', 'Acceso total a configuración y administración'),
('Standard', 'Acceso a visualización de analíticas sin privilegios de configuración')
ON CONFLICT (role_name) DO NOTHING;

-- 2. Tabla de Usuarios (Segura)
CREATE TABLE IF NOT EXISTS dw.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Almacenar hashes Bcrypt/Argon2
    full_name VARCHAR(200),
    role_id INTEGER REFERENCES dw.roles(role_id),
    status VARCHAR(20) DEFAULT 'Active', -- Active, Inactive, Locked
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    must_change_password BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bitácora de Acciones Administrativas (Auditoría)
CREATE TABLE IF NOT EXISTS dw.audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES dw.users(user_id),
    action VARCHAR(255) NOT NULL,
    module VARCHAR(100),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- NOTA: La inserción de usuarios iniciales se hará vía Python para generar los hashes correctamente.
