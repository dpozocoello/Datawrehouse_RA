-- Script de Estructura de Usuarios y Roles (DDL)
-- Dashboard ECO-SIEAA

CREATE SCHEMA IF NOT EXISTS dw;

-- 1. Tabla de Roles
CREATE TABLE IF NOT EXISTS dw.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 2. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS dw.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER REFERENCES dw.roles(role_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    must_change_password BOOLEAN DEFAULT TRUE,
    active BOOLEAN DEFAULT TRUE
);

-- 3. Tabla de Auditoría
CREATE TABLE IF NOT EXISTS dw.audit_logs (
    audit_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES dw.users(user_id),
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Rendimiento
CREATE INDEX IF NOT EXISTS idx_users_username ON dw.users(username);
CREATE INDEX IF NOT EXISTS idx_audit_user ON dw.audit_logs(user_id);
