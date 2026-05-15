# ⚙️ Ecosistema ETL Híbrido: Pentaho y Python (v1.5.1)

El sistema de integración de datos (ETL) utiliza una arquitectura de "Mando y Ejecución" basada en dos motores complementarios.

---

## 1. El Cerebro Visual: Pentaho Data Integration

Pentaho (PDI) actúa como el orquestador visual y gestor de conectividad para procesos que requieren lógica de flujo de datos (Stream) e interfaz gráfica de usuario para monitoreo.

### 1.1 Job Maestro: `JOB_CARGA_DWH_REGULARIZACION.kjb`
Ubicado en `F:\Datawrehouse_RA\Jobs\`, es el punto de control central.

**Flujo de Trabajo Operativo:**
1.  **Garantía de Referencia:** Ejecuta scripts SQL para restaurar valores `SK=0`.
2.  **Llamada a Potencia Python:** Dispara el orquestador `etl_main.py` para ingestas masivas.
3.  **Módulos KTR Especializados:**
    - `TRX_09_INGESTA_PAGOS_HIST.ktr`: Procesamiento de auditoría JBPM.
    - `TRX_06_INGESTA_SNAP.ktr`: Extracción de variables de intersección ambiental.
4.  **Sincronización:** Espera la finalización exitosa de los hilos de Python antes de proceder a la carga de Facts.

---

## 2. El Motor de Alto Rendimiento: Python Core

Python se utiliza para operaciones que demandan paralelismo, lógica de metadatos dinámica y manipulación masiva de datos (Big Data-ready).

### 2.1 Módulos de Ingesta (`ETL_p/ingesta/`)
- **`ingesta_all.py`**: Motor de transferencia masiva Oracle/Postgres -> Staging local.
- **`ingesta_waste_chemical.py`**: Implementa lógica `UNION ALL` para múltiples orígenes de sustancias y residuos, inyectando IDs de documentos relacionados.

### 2.2 Orquestador Central: `etl_main.py`
Proporciona una interfaz de línea de comandos (CLI) para control granular.

**Comandos Críticos:**
```bash
# Ejecución parcial (Ingesta Residuos/Químicos)
python etl_main.py --desde 24 --hasta 24

# Ejecución de Transformación v1.5
python etl_main.py --desde 25 --hasta 25
```

---

## 3. Interacción y Traspaso de Control

La arquitectura utiliza un modelo de **Semaforización por Salida de Código (Exit Codes)**:

1.  **Pentaho invoca Shell:** Ejecuta el comando python.
2.  **Python procesa:** Maneja internamente sus hilos de ejecución `ThreadPool`.
3.  **Reporte de Estado:**
    - `Exit 0`: Pentaho continúa al siguiente nodo del Job.
    - `Exit 1`: Pentaho aborta el Job y activa alertas de error.
4.  **Logging Cruzado:** Los logs de Python se redireccionan al `Spoon Logging Area` mediante el stream de salida estándar (stdout).

---

## 4. Matriz de Procesos y Herramientas

| Proceso | Tecnología | Motivo de Elección |
| :--- | :--- | :--- |
| Ingesta JBPM Pagos | Pentaho (KTR) | Lógica de flujo compleja y transformación de strings. |
| Ingesta SUIA/COA | Python (ingesta.py) | Velocidad en transferencia de red y paralelismo. |
| Inferencia Geográfica | SQL (Postgres) | Rendimiento óptimo en el motor de base de datos. |
| Integración Residuos | Híbrido (Py + SQL) | Flexibilidad de metadatos en Py, carga masiva en SQL. |

---

## 5. Prevención y Resolución de Conflictos

### 5.1 Bloqueos de Transacción y Visibilidad de Sesión
Debido a la naturaleza híbrida, se identificó un conflicto de visibilidad con las tablas `TEMP` en Pentaho. 
- **Solución implementada (v1.5.1):** Migración de la lógica de optimización a tablas de staging persistentes (`stg.tmp_dim_proyecto_optimized`). Esto evita el error "consulta sin resultados" y garantiza que el join de hechos sea estable entre diferentes sesiones de base de datos.
- **Mantenimiento PIDs:** Uso de `pg_terminate_backend` para liberar PIDs huérfanos antes de la carga masiva.

### 5.2 Optimización de Memoria
Pentaho limita el cache por paso a 10,000 filas para evitar `OutOfMemoryError`. Python utiliza generadores y `execute_batch` para manejar millones de registros con bajo consumo de RAM.

---

**Ingeniería de Datos:** Antigravity AI  
**Versión:** 1.5.1 (Estabilización Pentaho)  
**Estado:** Documentación Técnica Detallada
