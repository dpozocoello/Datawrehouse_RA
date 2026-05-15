# Technical Schema Report: Waste and Chemicals

## Table: dw.fact_waste_generation

| Column | Type |
| :--- | :--- |
| sk_proyecto | bigint |
| waste_generator_key | bigint |
| sk_tiempo | bigint |
| waste_type_key | bigint |
| dangerous_waste_key | bigint |
| danger_class_key | bigint |
| geo_location_key | bigint |
| quantity_generated | numeric |
| quantity_delivered | numeric |
| quantity_stored | numeric |
| unit | character varying |
| record_year | integer |

## Table: dw.dim_waste_generator

| Column | Type |
| :--- | :--- |
| waste_generator_key | bigint |
| waste_generator_id | bigint |
| generator_name | character varying |
| generator_type | character varying |
| province | character varying |
| canton | character varying |
| codigo | character varying |
| effective_from | timestamp without time zone |
| effective_to | timestamp without time zone |
| is_current | boolean |
| date_add | timestamp without time zone |
| date_update | timestamp without time zone |

## Table: dw.dim_waste_type

| Column | Type |
| :--- | :--- |
| waste_type_key | bigint |
| cawa_id | bigint |
| waste_key_code | character varying |
| waste_name | character varying |
| waste_status | boolean |

## Table: dw.dim_dangerous_waste

| Column | Type |
| :--- | :--- |
| dangerous_waste_key | bigint |
| dw_id | bigint |
| dangerous_code | character varying |
| description | character varying |
| regulation_reference | character varying |
| is_current | boolean |

## Table: dw.dim_dangerous_classification

| Column | Type |
| :--- | :--- |
| danger_class_key | bigint |
| class_id | bigint |
| danger_level | character varying |
| description | character varying |

## Table: dw.fact_chemical_application

| Column | Type |
| :--- | :--- |
| sk_proyecto | bigint |
| chemical_key | bigint |
| sk_tiempo | bigint |
| storage_key | bigint |
| geo_location_key | bigint |
| dose | numeric |
| dose_unit | character varying |
| application_method | character varying |
| area_covered | numeric |
| usage_year | integer |

## Table: dw.dim_chemical_substance

| Column | Type |
| :--- | :--- |
| chemical_key | bigint |
| chemical_id | bigint |
| substance_name | character varying |
| cas_number | character varying |
| classification | character varying |
| chemical_type | character varying |
| effective_from | timestamp without time zone |
| effective_to | timestamp without time zone |
| is_current | boolean |

## Table: dw.dim_chemical_storage

| Column | Type |
| :--- | :--- |
| storage_key | bigint |
| storage_id | bigint |
| storage_type | character varying |
| capacity | numeric |
| unit | character varying |
| location_description | character varying |

## Table: dw.fact_project_environmental_impact

| Column | Type |
| :--- | :--- |
| sk_proyecto | bigint |
| sk_tiempo | bigint |
| total_waste_volume | numeric |
| total_dangerous_waste_volume | numeric |
| total_chemical_dose | numeric |
| environmental_risk_score | numeric |

