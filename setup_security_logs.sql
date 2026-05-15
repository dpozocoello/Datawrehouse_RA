-- ==============================================================================
-- Proyecto: ECO-SIEAA - Control de Seguridad ISO 27001
-- Script: setup_security_logs.sql
-- Descripción: 
-- 1. Registro de logs de ingreso e intentos (con IP)
-- 2. Control de sesión única por usuario
-- ==============================================================================

-- 1. Tabla de Logs de Acceso (Ingresos e Intentos)
CREATE TABLE IF NOT EXISTS dw.login_logs (
    log_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50),
    status VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILED', 'BLOCKED_DUPLICATE'
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- 2. Tabla de Control de Sesiones Activas
CREATE TABLE IF NOT EXISTS dw.active_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES dw.users(user_id),
    ip_address VARCHAR(50),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_active_sessions_user ON dw.active_sessions(user_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_login_logs_username ON dw.login_logs(username);

COMMENT ON TABLE dw.login_logs IS 'Log de auditoría de accesos e intentos fallidos con trazabilidad de IP';
COMMENT ON TABLE dw.active_sessions IS 'Control de concurrencia para asegurar sesión única por usuario';
