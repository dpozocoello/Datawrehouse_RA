-- ==============================================================================
-- DDL v3 — Añade staging para online_payments_historical
-- ==============================================================================
-- 1. Crear tabla staging
CREATE TABLE IF NOT EXISTS stg.online_payments_historical_bi (
    id_online_payment_historical bigint,
    description character varying,
    project_id character varying,
    retired_value character varying,
    sender_ip character varying,
    tramit_number character varying,
    update_date timestamp without time zone,
    value_updated character varying,
    online_payment_id bigint,
    enabled boolean,
    user_create character varying,
    user_modification character varying,
    date_create character varying,
    date_modification character varying,
    reactivate integer,
    observations character varying,
    retired_value_1 character varying
);
-- Índices de búsqueda
CREATE INDEX IF NOT EXISTS idx_stg_oph_tramit ON stg.online_payments_historical_bi (tramit_number);
CREATE INDEX IF NOT EXISTS idx_stg_oph_project ON stg.online_payments_historical_bi (project_id);