# Guía de Instalación y Configuración — DWH RA
**Versión:** 1.0 | **Fecha:** 08 de mayo de 2026

## 1. Prerrequisitos de Infraestructura

*   **Motor de Base de Datos:** PostgreSQL 13 o superior.
*   **Sistema Operativo:** Windows Server 2019+ o Distribución Linux compatible.
*   **Python:** Versión 3.9+ (Para scripts de ingesta y utilitarios).
*   **Acceso de Red:** Conectividad al puerto 5432 del servidor origen SUIA/JBPM.

## 2. Preparación de la Base de Datos

1.  **Crear el Data Warehouse:**
    ```sql
    CREATE DATABASE dw_reg_v1;
    ```
2.  **Configurar Esquemas:**
    ```sql
    \c dw_reg_v1
    CREATE SCHEMA stg;
    CREATE SCHEMA dw;
    CREATE SCHEMA dm;
    CREATE SCHEMA ctl;
    ```

## 3. Despliegue Estructural (DDL)

El modelo completo se inicializa usando los scripts consolidados.
Navegue al directorio `D:\Datawrehouse_RA\` y ejecute usando `psql`:

```bash
# Carga de DDL base y tablas maestras (v1)
psql -U admin -d dw_reg_v1 -f ddl_base.sql

# Despliegue de actualización jerárquica y bridge (v2)
psql -U admin -d dw_reg_v1 -f v2\ddl_dwh_v2.sql

# Inicialización de Funciones Analíticas y Pagos (v3)
psql -U admin -d dw_reg_v1 -f v3\etl_carga_datos_v3.sql
```

## 4. Configuración del Entorno de Ejecución Python

Todos los scripts de control y validación residen en el directorio principal y requieren un entorno virtual configurado.

```bash
cd D:\Datawrehouse_RA\
python -m venv .venv
# Activar el entorno
.venv\Scripts\activate
# Instalar dependencias
pip install -r requirements.txt
```

## 5. Carga de Datos Inicial (Full Load)

La primera ejecución debe realizarse manualmente para poblar el histórico completo:

1. Modificar el archivo `.env` o las variables de entorno del sistema con las credenciales origen/destino (`DB_HOST`, `DB_USER`, `DB_PASS`).
2. Ejecutar la ingesta de las dimensiones de referencia (Archivos CSV locales como INEC, Cantones).
3. Lanzar el proceso maestro inicial:
    ```bash
    D:\Datawrehouse_RA\jobs\job_diario_dwh.bat
    ```
4. Validar que la tabla `dw.fact_proyecto_geografia` contenga aproximadamente 337,986 registros como métrica de éxito.
