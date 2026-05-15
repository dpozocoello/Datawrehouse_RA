import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ==============================================================================
# Proyecto: Registro Generador de Desechos (RGD)
# Script: rgd_etl_wrapper.py
# Descripción: Wrapper orientado a objetos para la ingesta de datos a DW.
# - Reemplaza los print() por logging estándar.
# - Parametriza credenciales (evitando hardcoding).
# - Incluye capa de validación Data Quality (Non-Breaking).
# - Retorna exit codes para que Pentaho orqueste adecuadamente.
# ==============================================================================

class RGDEtlPipeline:
    def __init__(self, db_url=None):
        """Inicializa el logger y la conexión a la base de datos."""
        # 1. Configuración de Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger("RGDEtlPipeline")
        self.logger.info("Inicializando pipeline ETL RGD...")

        # 2. Configuración de DB URL (Prioriza parámetro, luego Env Var)
        self.db_url = db_url or os.getenv(
            "RGD_DB_URL", 
            "postgresql://postgres:postgres@localhost:5432/dw_reg_v1" # Fallback local
        )
        
        try:
            self.engine = create_engine(self.db_url)
            self.logger.info("Conexión SQLAlchemy inicializada correctamente.")
        except Exception as e:
            self.logger.critical(f"Error al inicializar la conexión a DB: {e}")
            sys.exit(1)

        self.log_id = None
        self.rows_read = 0
        self.rows_written = 0
        self.rows_rejected = 0

    def start_etl_log(self, process_name):
        """Registra el inicio del proceso en dw.etl_log."""
        try:
            with self.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO dw.etl_log (process_name, status) 
                        VALUES (:proc, 'STARTED') 
                        RETURNING log_id
                    """),
                    {"proc": process_name}
                )
                self.log_id = result.scalar()
                self.logger.info(f"Registro de log iniciado con ID: {self.log_id}")
        except SQLAlchemyError as e:
            self.logger.warning(f"No se pudo escribir en etl_log: {e}")

    def update_etl_log(self, status, error_msg=None):
        """Actualiza el registro en dw.etl_log al finalizar."""
        if not self.log_id:
            return
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE dw.etl_log 
                        SET status = :status, 
                            rows_read = :read, 
                            rows_written = :written, 
                            rows_rejected = :rejected,
                            error_message = :err,
                            end_time = CURRENT_TIMESTAMP
                        WHERE log_id = :log_id
                    """),
                    {
                        "status": status,
                        "read": self.rows_read,
                        "written": self.rows_written,
                        "rejected": self.rows_rejected,
                        "err": error_msg,
                        "log_id": self.log_id
                    }
                )
        except SQLAlchemyError as e:
            self.logger.error(f"Error actualizando etl_log: {e}")

    def run_data_quality_checks(self, df):
        """Aplica reglas de negocio (Data Quality). Separa registros válidos de rechazados."""
        self.logger.info("Aplicando reglas de Data Quality...")
        
        if df.empty:
            return df, pd.DataFrame()

        # Regla 1: cantidad debe ser positiva o nula (ejemplo asumiendo columna 'cantidad')
        # Regla 2: codigo MAE no nulo
        # Se asumen columnas genéricas según el contexto; ajustar a columnas reales
        valid_mask = pd.Series(True, index=df.index)
        
        if 'cantidad' in df.columns:
            valid_mask &= (df['cantidad'] >= 0) | (df['cantidad'].isna())
        
        # Opcional: si existe columna 'codigo_proyecto', no debe estar vacía
        if 'codigo_proyecto' in df.columns:
            valid_mask &= df['codigo_proyecto'].notna()

        df_valid = df[valid_mask].copy()
        df_rejects = df[~valid_mask].copy()

        self.logger.info(f"Registros válidos: {len(df_valid)}, Registros rechazados: {len(df_rejects)}")
        return df_valid, df_rejects

    def log_rejects(self, df_rejects, reason="Fallo validación DQ"):
        """Inserta registros rechazados en la tabla staging_rejects."""
        if df_rejects.empty:
            return
            
        rejects_data = []
        for _, row in df_rejects.iterrows():
            rejects_data.append({
                "source_system": "RGD_PYTHON_WRAPPER",
                "record_payload": json.dumps(row.to_dict(), default=str),
                "reject_reason": reason
            })
            
        try:
            rejects_df = pd.DataFrame(rejects_data)
            rejects_df.to_sql('staging_rejects', con=self.engine, schema='dw', if_exists='append', index=False)
            self.rows_rejected += len(df_rejects)
            self.logger.info(f"Guardados {len(df_rejects)} registros en dw.staging_rejects")
        except Exception as e:
            self.logger.error(f"Error al registrar rechazos: {e}")

    def process_data(self, source_df, target_table):
        """Ejecuta el pipeline: DQ -> Inserts."""
        self.rows_read = len(source_df)
        
        try:
            df_valid, df_rejects = self.run_data_quality_checks(source_df)
            
            # Guardar rechazos (Non-Breaking)
            self.log_rejects(df_rejects)
            
            # Insertar registros válidos
            if not df_valid.empty:
                self.logger.info(f"Insertando {len(df_valid)} registros en dw.{target_table}...")
                # Uso de method='multi' para procesamiento por lotes eficiente en postgres
                df_valid.to_sql(target_table, con=self.engine, schema='dw', if_exists='append', index=False, method='multi', chunksize=1000)
                self.rows_written = len(df_valid)
                self.logger.info("Carga exitosa.")
            else:
                self.logger.warning("No hay registros válidos para insertar.")
                
            self.update_etl_log("SUCCESS")
            
        except Exception as e:
            self.logger.error(f"Error crítico en process_data: {e}")
            self.update_etl_log("FAILED", str(e))
            sys.exit(1) # Código de error para que Pentaho falle y alerte

def main():
    parser = argparse.ArgumentParser(description="Wrapper ETL RGD")
    parser.add_argument("--db-url", help="URL de conexión SQLAlchemy")
    parser.add_argument("--test-mode", action="store_true", help="Ejecuta en modo prueba")
    args = parser.parse_args()

    pipeline = RGDEtlPipeline(db_url=args.db_url)
    pipeline.start_etl_log("Ingesta_RGD_Fact")

    if args.test_mode:
        pipeline.logger.info("Modo de prueba activado. Generando datos simulados...")
        # Simulación de extracción de datos
        data = [
            {"waste_generator_key": 92911, "cantidad": 15.5, "codigo_proyecto": "MAE-RA-2026-580336"},
            {"waste_generator_key": 92912, "cantidad": -5.0, "codigo_proyecto": "MAE-RA-TEST"}, # Debe ser rechazado
            {"waste_generator_key": 92913, "cantidad": 10.0, "codigo_proyecto": None} # Rechazado si la regla está activa
        ]
        df = pd.DataFrame(data)
        # Aquí se insertaría en una tabla temporal o se ajustaría para coincidir con la estructura real de fact_waste_generation
        # Como es genérico, omitimos el insert real en modo test para no romper el esquema
        pipeline.logger.info("Simulación terminada.")
        pipeline.update_etl_log("SUCCESS", "Test mode execution")
        sys.exit(0)
    else:
        # Aquí iría la lógica real de extracción (Ej. leer de un CSV o tabla stage)
        pipeline.logger.warning("No hay origen de datos configurado para el modo producción en el script base.")
        pipeline.update_etl_log("SUCCESS", "No data source implemented yet")
        sys.exit(0)

if __name__ == "__main__":
    main()
