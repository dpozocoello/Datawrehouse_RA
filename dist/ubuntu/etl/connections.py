# ==============================================================================
# connections.py — Gestión de conexiones a bases de datos PostgreSQL
# ==============================================================================
# Proporciona un gestor de conexiones centralizado usando context managers
# para asegurar que las conexiones se cierren correctamente incluso si
# ocurre un error durante la ejecución del ETL.
#
# Uso típico:
#   with get_connection(CONN_DWH_LOCAL) as conn:
#       with conn.cursor() as cur:
#           cur.execute("SELECT 1")
# ==============================================================================

import psycopg2
from psycopg2 import sql, extras
from contextlib import contextmanager
from utils import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection(conn_params: dict, autocommit: bool = False):
    """
    Context manager que crea y gestiona una conexión PostgreSQL.

    Parámetros:
    -----------
    conn_params : dict
        Diccionario con las claves: host, port, database, user, password.
        Se obtiene de config.py (ej: config.CONN_DWH_LOCAL).
    autocommit : bool
        Si True, cada sentencia se ejecuta inmediatamente sin necesidad
        de llamar a conn.commit(). Útil para DDL y TRUNCATE.

    Yields:
    -------
    psycopg2.connection
        Conexión activa a la base de datos.

    Ejemplo:
    --------
    >>> from config import CONN_DWH_LOCAL
    >>> with get_connection(CONN_DWH_LOCAL) as conn:
    ...     with conn.cursor() as cur:
    ...         cur.execute("SELECT COUNT(1) FROM stg.suia_rcoa_bi")
    ...         print(cur.fetchone()[0])
    """
    conn = None
    db_name = conn_params.get("database", "desconocida")
    host = conn_params.get("host", "desconocido")
    try:
        logger.debug(f"Conectando a {db_name}@{host}:{conn_params.get('port', 5632)}...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = autocommit
        logger.debug(f"Conexión exitosa a {db_name}@{host}")
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error de conexión a {db_name}@{host}: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            logger.debug(f"Conexión cerrada: {db_name}@{host}")


def extract_to_staging(
    origen_params: dict,
    destino_params: dict,
    query_origen: str,
    tabla_destino: str,
    paso_nombre: str,
    batch_size: int = 1000
) -> int:
    """
    Función genérica de ingesta: extrae datos de un origen remoto y los
    carga en una tabla staging del DWH local.

    Implementa el patrón TRUNCATE + INSERT usado en todas las
    transformaciones de Pentaho (TRX_01 a TRX_09).

    Parámetros:
    -----------
    origen_params : dict
        Parámetros de conexión al servidor origen (ej: config.CONN_SUIA_ENLISY).
    destino_params : dict
        Parámetros de conexión al DWH local (ej: config.CONN_DWH_LOCAL).
    query_origen : str
        Consulta SQL SELECT que se ejecuta contra la base origen para
        extraer los datos. Debe retornar columnas compatibles con la
        tabla destino.
    tabla_destino : str
        Nombre completo de la tabla staging destino (ej: 'stg.suia_rcoa_bi').
    paso_nombre : str
        Nombre descriptivo del paso para los logs (ej: 'TRX_01_SUIA_RCOA').
    batch_size : int
        Número de filas por lote de inserción (default: 1000).

    Retorna:
    --------
    int
        Número total de filas insertadas.

    Proceso:
    --------
    1. Conecta al servidor origen y ejecuta la consulta de extracción
    2. Conecta al DWH local y ejecuta TRUNCATE sobre la tabla destino
    3. Inserta los datos en lotes usando execute_values (alta performance)
    4. Registra el conteo de filas en los logs

    Ejemplo:
    --------
    >>> filas = extract_to_staging(
    ...     origen_params=CONN_SUIA_ENLISY,
    ...     destino_params=CONN_DWH_LOCAL,
    ...     query_origen="SELECT * FROM coa_mae.tmp_rcoa_bi",
    ...     tabla_destino="stg.suia_rcoa_bi",
    ...     paso_nombre="TRX_01_SUIA_RCOA"
    ... )
    >>> print(f"Insertadas {filas} filas")
    """
    logger.info(f"[{paso_nombre}] Iniciando extracción...")
    total_filas = 0

    # ---- PASO 1: Extraer datos del origen ----
    with get_connection(origen_params) as conn_origen:
        with conn_origen.cursor() as cur_origen:
            logger.info(f"[{paso_nombre}] Ejecutando query de extracción...")
            cur_origen.execute(query_origen)

            # Obtener nombres de columnas del resultado
            col_names = [desc[0] for desc in cur_origen.description]
            num_cols = len(col_names)
            logger.info(f"[{paso_nombre}] Columnas extraídas: {num_cols} ({', '.join(col_names[:5])}...)")

            # ---- PASO 2: Truncar tabla destino ----
            with get_connection(destino_params) as conn_destino:
                with conn_destino.cursor() as cur_destino:
                    logger.info(f"[{paso_nombre}] TRUNCATE TABLE {tabla_destino}")
                    cur_destino.execute(f"TRUNCATE TABLE {tabla_destino}")
                    conn_destino.commit()

                    # ---- PASO 3: Insertar en lotes ----
                    # Construir la sentencia INSERT con placeholders
                    placeholders = ", ".join(["%s"] * num_cols)
                    insert_sql = f"INSERT INTO {tabla_destino} ({', '.join(col_names)}) VALUES %s"

                    while True:
                        rows = cur_origen.fetchmany(batch_size)
                        if not rows:
                            break

                        # execute_values es mucho más rápido que executemany
                        extras.execute_values(
                            cur_destino,
                            insert_sql,
                            rows,
                            page_size=batch_size
                        )
                        total_filas += len(rows)
                        logger.debug(f"[{paso_nombre}] Lote insertado: {len(rows)} filas (acumulado: {total_filas})")

                    conn_destino.commit()

    logger.info(f"[{paso_nombre}] ✓ Completado: {total_filas} filas cargadas en {tabla_destino}")
    return total_filas


def execute_sp(conn_params: dict, sp_call: str, paso_nombre: str) -> None:
    """
    Ejecuta un Stored Procedure o sentencia SQL en el DWH local.

    Parámetros:
    -----------
    conn_params : dict
        Parámetros de conexión (normalmente config.CONN_DWH_LOCAL).
    sp_call : str
        Sentencia SQL a ejecutar (ej: 'SELECT dw.sp_consolidar_staging()').
    paso_nombre : str
        Nombre descriptivo del paso para los logs.

    Ejemplo:
    --------
    >>> execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_consolidar_staging()", "SP_CONSOLIDAR")
    """
    logger.info(f"[{paso_nombre}] Ejecutando: {sp_call[:80]}...")
    with get_connection(conn_params) as conn:
        with conn.cursor() as cur:
            cur.execute(sp_call)
            conn.commit()
    logger.info(f"[{paso_nombre}] ✓ Completado")


def execute_sql(conn_params: dict, sql_text: str, paso_nombre: str) -> int:
    """
    Ejecuta una sentencia SQL arbitraria (UPDATE, CTE+UPDATE, etc.)
    y retorna el número de filas afectadas.

    Parámetros:
    -----------
    conn_params : dict
        Parámetros de conexión.
    sql_text : str
        Sentencia SQL completa a ejecutar.
    paso_nombre : str
        Nombre descriptivo del paso para los logs.

    Retorna:
    --------
    int
        Número de filas afectadas por la sentencia.
    """
    logger.info(f"[{paso_nombre}] Ejecutando SQL ({len(sql_text)} caracteres)...")
    with get_connection(conn_params) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
            filas = cur.rowcount if cur.rowcount > 0 else 0
            conn.commit()
    logger.info(f"[{paso_nombre}] ✓ Completado: {filas} filas afectadas")
    return filas
