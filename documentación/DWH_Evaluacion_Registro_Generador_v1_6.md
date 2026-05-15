# 📑 Informe de Evaluación Arquitectónica: Registro Generador de Desechos (v1.6)

**Arquitectura de Datos, Integración Multifuente y Propuesta Dimensional**

---

## 1. Análisis de Fuentes Transaccionales (Lineage)

La integración del **Registro Generador de Desechos** requiere la orquestación de datos provenientes de tres nodos críticos del ecosistema ministerial:

### 1.1 Esquema `coa_waste_generator_record` (Servidor SUIA 179)
- **Propósito:** Registro legal de los establecimientos generadores.
- **Entidades Clave:** `waste_generator_record_coa` (Cabecera), `waste_generator_record_project_licencing_coa` (Vinculación a Regularización), `waste_waste_generation_points` (Detalle de generación).
- **Información Obtenible:** Ubicación física (Provincia/Cantón), Fecha de Registro, Puntos de Generación y Cantidades estimadas.

### 1.2 Esquemas de Sustancias (`waste_dangerous` / `coa_chemical_sustances`)
- **Propósito:** Catálogos de peligrosidad y declaraciones de uso.
- **Entidades Clave:** `catalogs_waste` (NCI), `chemical_sustances_records` (Sustancias), `products_pqa` (Plaguicidas).
- **Información Obtenible:** Gravedad del residuo, clasificación toxicológica y métodos de aplicación.

### 1.3 Esquema `online_payment` (Servidor JBPM 226)
- **Propósito:** Gestión financiera de los trámites.
- **Entidades Clave:** `online_payments` (Cabecera), `online_payments_historical` (Trazabilidad de saldos).
- **Información Obtenible:** Montos pagados por concepto de Registro Generador, saldos remanentes y vinculación a procesos administrativos.

---

## 2. Modelado Dimensional Propuesto

Para soportar el análisis solicitado, se proponen las siguientes dimensiones y ajustes estructurales:

### 2.1 Nuevas Dimensiones (Conceptuales)
1. **`dw.dim_waste_generator` (ESTABLECIMIENTO):**
   - Atributos: RUC, Nombre del Establecimiento, Tipo de actividad generadora, Ubicación Geográfica.
2. **`dw.dim_waste_type` (RESIDUO):**
   - Atributos: Código NCI, Nombre del residuo, Nivel de peligrosidad, Reglamento asociado.
3. **`dw.dim_process_flow` (BPM):**
   - Atributos: Tipo de trámite (Registro Generador vs Declaración), Estado del flujo, Usuario responsable del proceso.

### 2.2 Dimensiones Afectadas (Ajustes)
1. **`dw.dim_proyecto` (VINCULACIÓN):**
   - **Cambio:** No afecta el concepto, pero requiere un puente (Bridge) para proyectos que tienen múltiples registros generadores asociados (Relación M:N).
2. **`dw.dim_tiempo`:**
   - **Cambio:** Sin afectación conceptual. Se inyectan hechos en fechas de "Emisión de Registro" y "Declaración Anual".

---

## 3. Integración de Hechos (Fact Tables)

Se define la evolución hacia dos métricas principales:

- **`dw.fact_waste_generation`:** Registro puntual de cantidades por residuo, proyecto y tiempo.
- **`dw.fact_payment_traceability` (NUEVA):** Basada en `online_payments_historical`. Permite ver la evolución del pago de un trámite de registro generador desde la orden inicial hasta la liquidación final.

---

## 4. Conclusiones Técnicas para Arquitecto e Ingeniero

1. **Unificación de IDs:** Es crítico utilizar el `internal_id` (numérico) para cruzar los datos del JBPM (pagos) con el SUIA (registros legales), ya que el código de proyecto (MAATE-...) tiene variaciones de formato entre bases.
2. **Gestión de Saldos:** El uso de `online_payments_historical` permitirá por primera vez realizar auditorías sobre pagos parciales o trámites fallidos de registros generadores.
3. **Optimización:** Se recomienda mantener la tabla `stg.tmp_dim_proyecto_optimized` (v1.5.1) para asegurar que el cruce entre los tres servidores (Pentaho-Python-Postgres) sea de alto rendimiento.

---

**Arquitecto e Ingeniero de Datos:** Antigravity AI  
**Versión:** 1.6  
**Estado:** Propuesta Técnica de Integración Finalizada
