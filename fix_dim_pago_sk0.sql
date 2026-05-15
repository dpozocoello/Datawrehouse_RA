-- Inyección de SK=0 en dim_pago para integridad referencial v1.6
INSERT INTO dw.dim_pago (sk_pago, tipo_pago, bank_code, transaction_type, sistema_origen)
VALUES (0, 'N/A', 'N/A', 'N/A', 'N/A')
ON CONFLICT (sk_pago) DO NOTHING;
