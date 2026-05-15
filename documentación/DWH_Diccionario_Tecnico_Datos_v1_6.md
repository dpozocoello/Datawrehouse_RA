# 📖 Diccionario Técnico de Datos: DRE Regularización Ambiental (v1.6)

Este documento detalla la estructura técnica exhaustiva de los esquemas `dw` y `stg` del Data Warehouse, bajo una arquitectura **Senior** diseñada para integridad forense y escalabilidad multi-nodo.

## 1. Relación de Capas y Gobernanza
- **Esquema `stg` (Staging/Bronze)**: Capa de aterrizaje volátil. Los datos se limpian y tipifican antes de su promoción.
- **Esquema `dw` (Warehouse/Gold)**: Capa dimensional inmutable (Modelo Estrella). Implementa **Slowly Changing Dimensions (SCD Type 2)** conceptualmente para trazas críticas.
- **Estrategia de Nulos**: Se utiliza la técnica de **Surrogate Key Zero (SK=0)** para evitar el filtrado accidental de hechos por falta de dimensiones (Inner Join protection).

### Tabla: `stg.consolidado_proyectos`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | text | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | text | YES | - |
| actividad_economica | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | text | YES | - |
| area_responsable_proyecto | text | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_ente | text | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | text | YES | - |
| estado_proceso | text | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | text | YES | - |
| estado_tarea | text | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proyecto | text | YES | - |
| intersecta_con | text | YES | - |
| areas_protegidas | text | YES | - |
| sistema | character varying | YES | - |
| nombre_zona | character varying | YES | - |
| finalizado_con_resolucion | character varying | YES | - |
| numero_resolucion | character varying | YES | - |
| fecha_resolucion | timestamp without time zone | YES | - |
| ente_acreditado | text | YES | - |
| estado_tramite | text | YES | - |
| id_area | integer | YES | - |
| superficie_proyecto | double precision | YES | - |
| estrategico | text | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.financial_transaction_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| fitr_id | integer | YES | - |
| codigo_proyecto | character varying | YES | - |
| fitr_transaction_amount | numeric | YES | - |
| fitr_paid_value | numeric | YES | - |
| fitr_transaction_number | character varying | YES | - |
| fitr_payment_type | integer | YES | - |
| payment_type_desc | character varying | YES | - |
| fitr_creation_date | timestamp without time zone | YES | - |
| fitr_status | boolean | YES | - |
| task_name | character varying | YES | - |
| processname | character varying | YES | - |
| processinstanceid | bigint | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.geographical_locations_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| gelo_id | integer | YES | - |
| gelo_name | character varying | YES | - |
| gelo_parent_id | integer | YES | - |
| gelo_codification_inec | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |

### Tabla: `stg.jbpm_4cat_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | character varying | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | character varying | YES | - |
| actividad_economica | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | text | YES | - |
| area_responsable_proyecto | text | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_ente | text | YES | - |
| provincia | text | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | character varying | YES | - |
| estado_proceso | text | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | character varying | YES | - |
| estado_tarea | text | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proyecto | text | YES | - |
| intersecta_con | text | YES | - |
| areas_protegidas | text | YES | - |
| sistema | text | YES | - |
| ente_acreditado | text | YES | - |
| estado_tramite | character varying | YES | - |
| estrategico | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.jbpm_hidro_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | character varying | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | character varying | YES | - |
| actividad_economica | character varying | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | character varying | YES | - |
| area_responsable_proyecto | character varying | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_ente | character varying | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | character varying | YES | - |
| estado_proceso | text | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | character varying | YES | - |
| estado_tarea | text | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | text | YES | - |
| estado_proyecto | text | YES | - |
| intersecta_con | text | YES | - |
| id_area | integer | YES | - |
| ente_acreditado | text | YES | - |
| estado_tramite | character varying | YES | - |
| estrategico | text | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.jbpm_sector_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | text | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | character varying | YES | - |
| actividad_economica | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | text | YES | - |
| area_responsable_proyecto | text | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | text | YES | - |
| tipo_ente | text | YES | - |
| provincia | text | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | text | YES | - |
| estado_proceso | text | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | character varying | YES | - |
| estado_tarea | text | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proyecto | character varying | YES | - |
| intersecta_con | text | YES | - |
| areas_protegidas | text | YES | - |
| sistema | text | YES | - |
| ente_acreditado | text | YES | - |
| estado_tramite | text | YES | - |
| estrategico | text | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.jbpm_snap_variables`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | text | YES | - |
| processinstanceid | bigint | YES | - |
| nombre_proceso | text | YES | - |
| estado_proceso | integer | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |

### Tabla: `stg.online_payments_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| online_payment_id | integer | YES | - |
| project_id | character varying | YES | - |
| tramit_number | character varying | YES | - |
| convenience_number | character varying | YES | - |
| bank_code | character varying | YES | - |
| payment_value | numeric | YES | - |
| date_hour_transaction | timestamp without time zone | YES | - |
| transaction_type | character varying | YES | - |
| transaction_state | boolean | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.online_payments_historical_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| id_online_payment_historical | bigint | YES | - |
| description | character varying | YES | - |
| project_id | character varying | YES | - |
| retired_value | character varying | YES | - |
| sender_ip | character varying | YES | - |
| tramit_number | character varying | YES | - |
| update_date | timestamp without time zone | YES | - |
| value_updated | character varying | YES | - |
| online_payment_id | bigint | YES | - |
| enabled | boolean | YES | - |
| user_create | character varying | YES | - |
| user_modification | character varying | YES | - |
| date_create | character varying | YES | - |
| date_modification | character varying | YES | - |
| reactivate | integer | YES | - |
| observations | character varying | YES | - |
| retired_value_1 | character varying | YES | - |

### Tabla: `stg.stg_chemical_storage`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| storage_id | bigint | YES | - |
| storage_type | text | YES | - |
| capacity | text | YES | - |
| unit | text | YES | - |
| location_description | text | YES | - |

### Tabla: `stg.stg_chemical_substance`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| chemical_id | bigint | YES | - |
| substance_name | text | YES | - |
| cas_number | text | YES | - |
| classification | text | YES | - |
| chemical_type | text | YES | - |

### Tabla: `stg.stg_dangerous_classification`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| class_id | bigint | YES | - |
| danger_level | text | YES | - |
| description | text | YES | - |

### Tabla: `stg.stg_dangerous_waste`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| dw_id | bigint | YES | - |
| dangerous_code | text | YES | - |
| description | text | YES | - |
| regulation_reference | text | YES | - |

### Tabla: `stg.stg_fact_chemical_application`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| project_id | double precision | YES | - |
| chemical_id | bigint | YES | - |
| date_applied | timestamp without time zone | YES | - |
| storage_id | text | YES | - |
| location_id | text | YES | - |
| dose | double precision | YES | - |
| dose_unit | text | YES | - |
| application_method | text | YES | - |
| area_covered | double precision | YES | - |
| usage_year | bigint | YES | - |

### Tabla: `stg.stg_fact_waste_generation`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| project_id | double precision | YES | - |
| waste_generator_id | bigint | YES | - |
| date_generated | timestamp without time zone | YES | - |
| waste_type_id | bigint | YES | - |
| dangerous_waste_id | text | YES | - |
| danger_class_id | text | YES | - |
| location_id | text | YES | - |
| quantity_generated | double precision | YES | - |
| quantity_delivered | double precision | YES | - |
| quantity_stored | double precision | YES | - |
| unit | text | YES | - |
| record_year | double precision | YES | - |

### Tabla: `stg.stg_waste_generator`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| waste_generator_id | bigint | YES | - |
| generator_name | text | YES | - |
| generator_type | text | YES | - |
| province | text | YES | - |
| canton | text | YES | - |
| date_add | timestamp without time zone | YES | - |
| date_update | timestamp without time zone | YES | - |

### Tabla: `stg.stg_waste_type`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| cawa_id | bigint | YES | - |
| waste_key_code | text | YES | - |
| waste_name | text | YES | - |
| waste_status | boolean | YES | - |

### Tabla: `stg.suia_areas_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| area_id | integer | YES | - |
| area_name | character varying | YES | - |
| area_abbreviation | character varying | YES | - |
| area_parent_id | integer | YES | - |
| zone_id | integer | YES | - |
| area_status | boolean | YES | - |
| area_campus | character varying | YES | - |
| arty_id | integer | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| gelo_id | integer | YES | - |

### Tabla: `stg.suia_coa_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | text | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | text | YES | - |
| actividad_economica | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | character varying | YES | - |
| area_responsable_proyecto | character varying | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_ente | character varying | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | character varying | YES | - |
| estado_proceso | character varying | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | character varying | YES | - |
| estado_tarea | character varying | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proyecto | character varying | YES | - |
| intersecta_con | text | YES | - |
| areas_protegidas | text | YES | - |
| sistema | character varying | YES | - |
| nombre_zona | character varying | YES | - |
| finalizado_con_resolucion | character varying | YES | - |
| numero_resolucion | character varying | YES | - |
| fecha_resolucion | timestamp without time zone | YES | - |
| id_area | integer | YES | - |
| estado_tramite | character varying | YES | - |
| superficie_proyecto | double precision | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `stg.suia_rcoa_bi`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | text | YES | - |
| fecha_registro | date | YES | - |
| codigo_actividad | text | YES | - |
| actividad_economica | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | character varying | YES | - |
| area_responsable_proyecto | character varying | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_ente | character varying | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| proceso | character varying | YES | - |
| estado_proceso | character varying | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| tarea | character varying | YES | - |
| estado_tarea | character varying | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proyecto | character varying | YES | - |
| intersecta_con | text | YES | - |
| areas_protegidas | text | YES | - |
| sistema | character varying | YES | - |
| nombre_zona | character varying | YES | - |
| finalizado_con_resolucion | character varying | YES | - |
| numero_resolucion | character varying | YES | - |
| fecha_resolucion | timestamp without time zone | YES | - |
| id_area | integer | YES | - |
| estado_tramite | character varying | YES | - |
| superficie_proyecto | double precision | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| origen | character varying | YES | - |

### Tabla: `dw.bridge_interseccion_ambiental`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | integer | NO | - |
| sk_capa | integer | NO | - |
| detalle_interseccion | text | NO | - |

### Tabla: `dw.dim_actividad`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_actividad | integer | NO | - |
| codigo_actividad | text | YES | - |
| actividad_economica | text | YES | - |

### Tabla: `dw.dim_area`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_area | integer | NO | - |
| id_area | integer | YES | - |
| nombre_area | character varying | YES | - |
| abreviatura_area | character varying | YES | - |
| id_area_padre | integer | YES | - |
| zona | character varying | YES | - |
| campus | character varying | YES | - |
| estado_area | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |

### Tabla: `dw.dim_capa_ambiental`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_capa | integer | NO | - |
| id_layer_origen | integer | YES | - |
| nombre_capa | character varying | YES | - |
| descripcion_capa | text | YES | - |
| categoria | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |

### Tabla: `dw.dim_chemical_storage`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| storage_key | bigint | NO | - |
| storage_id | bigint | NO | - |
| storage_type | character varying | YES | - |
| capacity | numeric | YES | - |
| unit | character varying | YES | - |
| location_description | character varying | YES | - |

### Tabla: `dw.dim_chemical_substance`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| chemical_key | bigint | NO | - |
| chemical_id | bigint | NO | - |
| substance_name | character varying | YES | - |
| cas_number | character varying | YES | - |
| classification | character varying | YES | - |
| chemical_type | character varying | YES | - |
| effective_from | timestamp without time zone | YES | - |
| effective_to | timestamp without time zone | YES | - |
| is_current | boolean | YES | - |

### Tabla: `dw.dim_dangerous_classification`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| danger_class_key | bigint | NO | - |
| class_id | bigint | NO | - |
| danger_level | character varying | YES | - |
| description | character varying | YES | - |

### Tabla: `dw.dim_dangerous_waste`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| dangerous_waste_key | bigint | NO | - |
| dw_id | bigint | NO | - |
| dangerous_code | character varying | YES | - |
| description | character varying | YES | - |
| regulation_reference | character varying | YES | - |
| is_current | boolean | YES | - |

### Tabla: `dw.dim_estado`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_estado | integer | NO | - |
| estado_proceso | text | YES | - |
| estado_proyecto | text | YES | - |
| estado_tramite | text | YES | - |

### Tabla: `dw.dim_geografia`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_geografia | integer | NO | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| sk_padre | integer | YES | - |
| nivel | character varying | YES | - |

### Tabla: `dw.dim_pago`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_pago | integer | NO | - |
| tipo_pago | character varying | YES | - |
| bank_code | character varying | YES | - |
| transaction_type | character varying | YES | - |
| sistema_origen | character varying | YES | - |

### Tabla: `dw.dim_process_flow` (v1.6)

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proceso | integer | NO | - |
| process_name | character varying | YES | - |
| process_type | character varying | YES | - |
| process_status | character varying | YES | - |

### Tabla: `dw.dim_proponente`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proponente | integer | NO | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | text | YES | - |

### Tabla: `dw.dim_proyecto`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | integer | NO | - |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| resumen_proyecto | text | YES | - |
| direccion_proyecto | text | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_ente | text | YES | - |
| sistema | character varying | YES | - |
| estrategico | text | YES | - |
| area_responsable | text | YES | - |

### Tabla: `dw.dim_tiempo`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_tiempo | integer | NO | - |
| fecha | date | YES | - |
| anio | integer | YES | - |
| mes | integer | YES | - |
| dia | integer | YES | - |
| trimestre | integer | YES | - |
| nombre_mes | character varying | YES | - |
| dia_semana | character varying | YES | - |

### Tabla: `dw.dim_usuario`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_usuario | integer | NO | - |
| usuario_tarea | character varying | YES | - |

### Tabla: `dw.dim_waste_generator`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| waste_generator_key | bigint | NO | - |
| waste_generator_id | bigint | NO | - |
| generator_name | character varying | YES | - |
| generator_type | character varying | YES | - |
| ruc_generator | character varying | YES | [v1.6] RUC del proponente |
| province | character varying | YES | - |
| canton | character varying | YES | - |
| codigo | character varying | YES | - |
| effective_from | timestamp without time zone | YES | - |
| effective_to | timestamp without time zone | YES | - |
| is_current | boolean | YES | - |
| date_add | timestamp without time zone | YES | - |
| date_update | timestamp without time zone | YES | - |

### Tabla: `dw.dim_waste_type`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| waste_type_key | bigint | NO | - |
| cawa_id | bigint | NO | - |
| waste_key_code | character varying | YES | - |
| waste_name | character varying | YES | - |
| waste_status | boolean | YES | - |

### Tabla: `dw.fact_chemical_application`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | bigint | NO | - |
| chemical_key | bigint | NO | - |
| sk_tiempo | bigint | NO | - |
| storage_key | bigint | YES | - |
| geo_location_key | bigint | YES | - |
| dose | numeric | YES | - |
| dose_unit | character varying | YES | - |
| application_method | character varying | YES | - |
| area_covered | numeric | YES | - |
| usage_year | integer | YES | - |

### Tabla: `dw.fact_pago`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| id_fact_pago | integer | NO | - |
| sk_proyecto | integer | YES | - |
| sk_pago | integer | YES | - |
| sk_fecha_pago | integer | YES | - |
| monto_transaccion | numeric | YES | - |
| monto_pagado | numeric | YES | - |
| numero_transaccion | character varying | YES | - |
| numero_tramite | character varying | YES | - |
| tarea_bpm | character varying | YES | - |
| proceso_bpm | character varying | YES | - |
| origen | character varying | YES | - |
| id_transaccion_origen | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| secuencia_pago | integer | YES | - |
| es_deposito_inicial | boolean | YES | - |
| monto_acumulado | numeric | YES | - |

### Tabla: `dw.fact_payment_traceability` (v1.6)

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| id_trace | integer | NO | PK Autoincremental |
| sk_proyecto | integer | YES | FK a dim_proyecto |
| sk_pago | integer | YES | FK a dim_pago (SK=0 si no existe) |
| sk_tiempo | integer | YES | FK a dim_tiempo |
| id_online_payment_historical | bigint | YES | ID origen JBPM |
| retired_value | numeric | YES | Monto debitado/retirado |
| value_updated | numeric | YES | Saldo actualizado |
| delta_value | numeric | YES | Variación (retired - updating) |
| update_date | timestamp | YES | Fecha de la trazabilidad |
| description | text | YES | Observaciones del sistema |

### Tabla: `dw.fact_project_environmental_impact`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | bigint | NO | - |
| sk_tiempo | bigint | NO | - |
| total_waste_volume | numeric | YES | - |
| total_dangerous_waste_volume | numeric | YES | - |
| total_chemical_dose | numeric | YES | - |
| environmental_risk_score | numeric | YES | - |

### Tabla: `dw.fact_proyecto_geografia`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | integer | NO | - |
| sk_geografia | integer | NO | - |
| es_principal | boolean | YES | - |
| fecha_carga | timestamp without time zone | YES | - |

### Tabla: `dw.fact_regularizacion`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| id_fact | integer | NO | - |
| sk_proyecto | integer | YES | - |
| sk_proponente | integer | YES | - |
| sk_actividad | integer | YES | - |
| sk_geografia | integer | YES | - |
| sk_usuario | integer | YES | - |
| sk_estado | integer | YES | - |
| sk_fecha_registro | integer | YES | - |
| interseccion_snap | text | YES | - |
| areas_protegidas | text | YES | - |
| superficie_proyecto | double precision | YES | - |
| id_area | integer | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| proceso | text | YES | - |
| tarea | text | YES | - |
| nombre_zona | character varying | YES | - |
| finalizado_con_resolucion | character varying | YES | - |
| numero_resolucion | character varying | YES | - |
| fecha_resolucion | timestamp without time zone | YES | - |
| ente_acreditado | text | YES | - |
| origen | character varying | YES | - |
| fecha_carga | timestamp without time zone | YES | - |
| sk_area | integer | YES | - |

### Tabla: `dw.fact_waste_generation`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| sk_proyecto | bigint | NO | - |
| waste_generator_key | bigint | NO | - |
| sk_tiempo | bigint | NO | - |
| waste_type_key | bigint | NO | - |
| dangerous_waste_key | bigint | YES | - |
| danger_class_key | bigint | YES | - |
| geo_location_key | bigint | YES | - |
| quantity_generated | numeric | YES | - |
| quantity_delivered | numeric | YES | - |
| quantity_stored | numeric | YES | - |
| unit | character varying | YES | - |
| record_year | integer | YES | - |

### Tabla: `dw.v_dashboard_regularizacion`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| id_fact | integer | YES | - |
| origen | character varying | YES | - |
| codigo_proyecto | character varying | YES | - |
| nombre_proyecto | text | YES | - |
| tipo_permiso_ambiental | character varying | YES | - |
| tipo_sector | character varying | YES | - |
| tipo_ente | text | YES | - |
| sistema | character varying | YES | - |
| estrategico | text | YES | - |
| ced_ruc_proponente | character varying | YES | - |
| nombre_proponente | text | YES | - |
| codigo_actividad | text | YES | - |
| actividad_economica | text | YES | - |
| provincia | character varying | YES | - |
| canton | character varying | YES | - |
| parroquia | character varying | YES | - |
| oficina_tecnica | character varying | YES | - |
| zona_administrativa | character varying | YES | - |
| sede_campus | character varying | YES | - |
| usuario_tarea | character varying | YES | - |
| estado_proceso | text | YES | - |
| estado_proyecto | text | YES | - |
| estado_tramite | text | YES | - |
| fecha_registro | date | YES | - |
| anio_registro | integer | YES | - |
| mes_registro | character varying | YES | - |
| trimestre_registro | integer | YES | - |
| interseccion_snap | text | YES | - |
| areas_protegidas | text | YES | - |
| superficie_proyecto | double precision | YES | - |
| id_area | integer | YES | - |
| fecha_inicio_proceso | timestamp without time zone | YES | - |
| fecha_fin_proceso | timestamp without time zone | YES | - |
| duracion_proceso_dias | numeric | YES | - |
| fecha_inicio_tarea | timestamp without time zone | YES | - |
| fecha_fin_tarea | timestamp without time zone | YES | - |
| duracion_tarea_horas | numeric | YES | - |
| finalizado_con_resolucion | character varying | YES | - |
| numero_resolucion | character varying | YES | - |
| fecha_resolucion | timestamp without time zone | YES | - |
| es_resolucion | integer | YES | - |

### Tabla: `dw.v_integridad_dashboard`

| Columna | Tipo de Dato | Nulable | Propósito |
| :--- | :--- | :--- | :--- |
| origen | text | YES | - |
| total_produccion | bigint | YES | - |
| total_dwh | bigint | YES | - |
| diferencia | bigint | YES | - |
| porcentaje_integridad | numeric | YES | - |
