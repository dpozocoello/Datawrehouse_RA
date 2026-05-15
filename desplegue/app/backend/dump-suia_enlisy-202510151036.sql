--
-- PostgreSQL database dump
--

\restrict 6z69kfHsywULYz40w2ZLBQQim0jdqe7GWpgucyaXkzLbTTbgXoCnQcIqxjaAf7Q

-- Dumped from database version 10.15
-- Dumped by pg_dump version 17.6

-- Started on 2025-10-15 10:36:17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 347 (class 2615 OID 43687447)
-- Name: coa_waste_generator_update; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA coa_waste_generator_update;


ALTER SCHEMA coa_waste_generator_update OWNER TO postgres;

--
-- TOC entry 16268 (class 0 OID 0)
-- Dependencies: 347
-- Name: SCHEMA coa_waste_generator_update; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA coa_waste_generator_update IS 'Esquema que almacena Información de Registro Generador de Residuos o Desechos Especiales y/o Peligrosos s ';


SET default_tablespace = '';

--
-- TOC entry 4529 (class 1259 OID 43687448)
-- Name: coordinates_coa_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.coordinates_coa_update (
    coor_id integer NOT NULL,
    coor_status boolean DEFAULT true NOT NULL,
    coor_description character varying(255),
    coor_order integer,
    coor_x double precision,
    coor_y double precision,
    rpsh_id integer,
    coor_zone character varying(3),
    coor_update_number integer DEFAULT 0,
    coor_creation_date timestamp(6) without time zone DEFAULT now() NOT NULL,
    coor_creator_user character varying(255) NOT NULL,
    coor_date_update timestamp(6) without time zone,
    coor_user_update character varying(255),
    coor_observation_bd character varying(255)
)
WITH (autovacuum_enabled='true');


ALTER TABLE coa_waste_generator_update.coordinates_coa_update OWNER TO postgres;

--
-- TOC entry 16270 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_id IS 'Clave Primaria';


--
-- TOC entry 16271 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_status IS 'Estado del registro';


--
-- TOC entry 16272 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_description; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_description IS 'Descripción coordenada';


--
-- TOC entry 16273 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_order; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_order IS 'Order de la coordenada';


--
-- TOC entry 16274 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_x; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_x IS 'coordenada x';


--
-- TOC entry 16275 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_y; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_y IS 'coordenada y';


--
-- TOC entry 16276 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.rpsh_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.rpsh_id IS 'clave foranea de la tabla
coa_waste_generator_update.recovery_point_shapes_coa_update';


--
-- TOC entry 16277 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_zone; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_zone IS 'Zona de la coordenada';


--
-- TOC entry 16278 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_update_number; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_update_number IS 'Numero de actualización de la coordenada';


--
-- TOC entry 16279 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_creation_date IS 'Fecha de Creación';


--
-- TOC entry 16280 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_creator_user IS 'Usuario que crea';


--
-- TOC entry 16281 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_date_update IS 'Fecha actualización';


--
-- TOC entry 16282 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16283 (class 0 OID 0)
-- Dependencies: 4529
-- Name: COLUMN coordinates_coa_update.coor_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.coordinates_coa_update.coor_observation_bd IS 'Campo de observación para base de datos';


--
-- TOC entry 4530 (class 1259 OID 43687457)
-- Name: coordinates_coa_update_coor_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.coordinates_coa_update_coor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.coordinates_coa_update_coor_id_seq OWNER TO postgres;

--
-- TOC entry 16285 (class 0 OID 0)
-- Dependencies: 4530
-- Name: coordinates_coa_update_coor_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.coordinates_coa_update_coor_id_seq OWNED BY coa_waste_generator_update.coordinates_coa_update.coor_id;


--
-- TOC entry 4531 (class 1259 OID 43687459)
-- Name: documents_coa_waste_generator_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.documents_coa_waste_generator_update (
    dowa_id integer NOT NULL,
    dowa_name character varying(255),
    dowa_mime character varying(255),
    doty_id integer,
    dowa_status boolean DEFAULT true NOT NULL,
    dowa_alfresco_id character varying(255),
    dowa_extesion character varying(255),
    dowa_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    dowa_date_update timestamp without time zone,
    dowa_creator_user character varying(255),
    dowa_user_update character varying(255),
    dowa_observation_bd character varying(255),
    ware_id integer,
    dowa_type_user integer,
    dowa_table_id integer,
    dowa_description character varying(255),
    dowa_table_class character varying(255),
    dowa_code_public character varying(255),
    dowa_process_instance_id integer
)
WITH (autovacuum_enabled='true');


ALTER TABLE coa_waste_generator_update.documents_coa_waste_generator_update OWNER TO postgres;

--
-- TOC entry 16287 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_id IS 'pk de la tabla';


--
-- TOC entry 16288 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_name; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_name IS 'Nombre documento';


--
-- TOC entry 16289 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.doty_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.doty_id IS 'fk Tipo documento';


--
-- TOC entry 16290 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_status IS 'estatus del documento';


--
-- TOC entry 16291 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_alfresco_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_alfresco_id IS 'clave de documento en alfresco';


--
-- TOC entry 16292 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_extesion; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_extesion IS 'Extension del docuemnto';


--
-- TOC entry 16293 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_creation_date IS 'Fecha de Creacion';


--
-- TOC entry 16294 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_date_update IS 'Fecha de actualizacion';


--
-- TOC entry 16295 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_creator_user IS 'Usuario que crea';


--
-- TOC entry 16296 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16297 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_observation_bd IS 'Observacion de modificacion de BD';


--
-- TOC entry 16298 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.ware_id IS 'Id del generador';


--
-- TOC entry 16299 (class 0 OID 0)
-- Dependencies: 4531
-- Name: COLUMN documents_coa_waste_generator_update.dowa_type_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.documents_coa_waste_generator_update.dowa_type_user IS 'Tipo de usuario que almacena. 1 operador, 2 tecnico, 3 director';


--
-- TOC entry 4532 (class 1259 OID 43687467)
-- Name: documents_coa_waste_generator_update_dowa_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq OWNER TO postgres;

--
-- TOC entry 16301 (class 0 OID 0)
-- Dependencies: 4532
-- Name: documents_coa_waste_generator_update_dowa_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq OWNED BY coa_waste_generator_update.documents_coa_waste_generator_update.dowa_id;


--
-- TOC entry 4533 (class 1259 OID 43687479)
-- Name: generation_points_waste_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.generation_points_waste_update (
    gewa_id integer NOT NULL,
    gepo_id integer,
    wwgp_id integer,
    gewa_status boolean DEFAULT true,
    gewa_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    gewa_creator_user character varying(1024),
    gewa_date_update timestamp without time zone,
    gewa_user_update character varying(1024),
    gewa_observation_bd character varying(1024)
);


ALTER TABLE coa_waste_generator_update.generation_points_waste_update OWNER TO postgres;

--
-- TOC entry 16303 (class 0 OID 0)
-- Dependencies: 4533
-- Name: COLUMN generation_points_waste_update.gewa_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.generation_points_waste_update.gewa_id IS 'clave primaria';


--
-- TOC entry 16304 (class 0 OID 0)
-- Dependencies: 4533
-- Name: COLUMN generation_points_waste_update.gepo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.generation_points_waste_update.gepo_id IS 'clave foranea ';


--
-- TOC entry 16305 (class 0 OID 0)
-- Dependencies: 4533
-- Name: COLUMN generation_points_waste_update.wwgp_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.generation_points_waste_update.wwgp_id IS 'clave foranea';


--
-- TOC entry 16306 (class 0 OID 0)
-- Dependencies: 4533
-- Name: COLUMN generation_points_waste_update.gewa_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.generation_points_waste_update.gewa_creation_date IS 'Fecha creación';


--
-- TOC entry 4534 (class 1259 OID 43687487)
-- Name: generation_points_waste_update_gewa_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.generation_points_waste_update_gewa_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.generation_points_waste_update_gewa_id_seq OWNER TO postgres;

--
-- TOC entry 16308 (class 0 OID 0)
-- Dependencies: 4534
-- Name: generation_points_waste_update_gewa_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.generation_points_waste_update_gewa_id_seq OWNED BY coa_waste_generator_update.generation_points_waste_update.gewa_id;


--
-- TOC entry 4535 (class 1259 OID 43687489)
-- Name: recovery_point_shapes_coa_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.recovery_point_shapes_coa_update (
    rpsh_id integer NOT NULL,
    rpsh_status boolean DEFAULT true NOT NULL,
    repo_id integer,
    shty_id integer,
    rpsh_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    rpsh_creator_user character varying(1024),
    rpsh_date_update timestamp without time zone,
    rpsh_user_update character varying(1024),
    rpsh_observation_bd character varying(1024)
);


ALTER TABLE coa_waste_generator_update.recovery_point_shapes_coa_update OWNER TO postgres;

--
-- TOC entry 16310 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_id IS 'Clave primaria ';


--
-- TOC entry 16311 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_status IS 'Estado del registro';


--
-- TOC entry 16312 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.repo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.repo_id IS 'Clave foranea de la tabla
coa_waste_generator_update.recovery_points_coa_update';


--
-- TOC entry 16313 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.shty_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.shty_id IS 'Clave foranea de la tabla suia_iii.shape_types';


--
-- TOC entry 16314 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_creation_date IS 'Fecha creación';


--
-- TOC entry 16315 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_creator_user IS 'Usuario que crea';


--
-- TOC entry 16316 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_date_update IS 'Fecha de actualización';


--
-- TOC entry 16317 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16318 (class 0 OID 0)
-- Dependencies: 4535
-- Name: COLUMN recovery_point_shapes_coa_update.rpsh_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_observation_bd IS 'Observación para base de datos';


--
-- TOC entry 4536 (class 1259 OID 43687497)
-- Name: recovery_point_shapes_coa_update_rpsh_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq OWNER TO postgres;

--
-- TOC entry 16320 (class 0 OID 0)
-- Dependencies: 4536
-- Name: recovery_point_shapes_coa_update_rpsh_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq OWNED BY coa_waste_generator_update.recovery_point_shapes_coa_update.rpsh_id;


--
-- TOC entry 4537 (class 1259 OID 43687499)
-- Name: recovery_points_coa_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.recovery_points_coa_update (
    repo_id integer NOT NULL,
    repo_status boolean DEFAULT true NOT NULL,
    repo_name character varying(255) NOT NULL,
    repo_phone character varying(255),
    repo_email character varying(255),
    repo_address character varying(255),
    gelo_id integer,
    ware_id integer,
    repo_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    repo_creator_user character varying(1024),
    repo_date_update timestamp without time zone,
    repo_user_update character varying(1024),
    repo_observation_bd character varying(1024),
    gepo_id integer,
    repo_generation_points_other character varying(255)
);


ALTER TABLE coa_waste_generator_update.recovery_points_coa_update OWNER TO postgres;

--
-- TOC entry 16322 (class 0 OID 0)
-- Dependencies: 4537
-- Name: TABLE recovery_points_coa_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.recovery_points_coa_update IS 'Puntos de Generación';


--
-- TOC entry 16323 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_id IS 'Clave Primaria';


--
-- TOC entry 16324 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_status IS 'Estado del Registro';


--
-- TOC entry 16325 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_name; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_name IS 'Nombre del comntacto del punto de referencia';


--
-- TOC entry 16326 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_phone; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_phone IS 'Telefono del comntacto del punto de referencia';


--
-- TOC entry 16327 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_email; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_email IS 'Email del comntacto del punto de referencia';


--
-- TOC entry 16328 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_address; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_address IS 'Dirección del comntacto del punto de referencia';


--
-- TOC entry 16329 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.gelo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.gelo_id IS 'Clave foranea de la tabla ubicación geografica';


--
-- TOC entry 16330 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.ware_id IS 'clave foranea de la tabla 
coa_waste_generator_update.waste_generator_record_coa';


--
-- TOC entry 16331 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_creation_date IS 'Fecha creación';


--
-- TOC entry 16332 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_creator_user IS 'Usuario que crea';


--
-- TOC entry 16333 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_date_update IS 'Fecha de actualización';


--
-- TOC entry 16334 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_user_update IS 'Usuario actualiza';


--
-- TOC entry 16335 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_observation_bd IS 'Observación utilizado por bdd';


--
-- TOC entry 16336 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.gepo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.gepo_id IS 'PuntoGeneracionRgdRcoa';


--
-- TOC entry 16337 (class 0 OID 0)
-- Dependencies: 4537
-- Name: COLUMN recovery_points_coa_update.repo_generation_points_other; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.recovery_points_coa_update.repo_generation_points_other IS 'Otro Punto Generacion';


--
-- TOC entry 4538 (class 1259 OID 43687507)
-- Name: recovery_points_coa_update_repo_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.recovery_points_coa_update_repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.recovery_points_coa_update_repo_id_seq OWNER TO postgres;

--
-- TOC entry 16339 (class 0 OID 0)
-- Dependencies: 4538
-- Name: recovery_points_coa_update_repo_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.recovery_points_coa_update_repo_id_seq OWNED BY coa_waste_generator_update.recovery_points_coa_update.repo_id;


--
-- TOC entry 4539 (class 1259 OID 43687509)
-- Name: waste_generaton_coa_project_linkage; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage (
    rgpl_id integer NOT NULL,
    rgpl_source text NOT NULL,
    hwge_id integer,
    ware_id integer,
    pren_id integer,
    prco_id integer,
    rgpl_linkage_date timestamp without time zone DEFAULT now() NOT NULL,
    rgpl_linked_by character varying(255) NOT NULL,
    rgpl_comments text,
    rgpl_manual_linkage boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_rgpl_source_consistency CHECK ((((rgpl_source = 'SITEAA'::text) AND (hwge_id IS NOT NULL) AND (ware_id IS NULL) AND (pren_id IS NOT NULL) AND (prco_id IS NULL)) OR ((rgpl_source = 'COA'::text) AND (ware_id IS NOT NULL) AND (hwge_id IS NULL) AND (prco_id IS NOT NULL) AND (pren_id IS NULL)))),
    CONSTRAINT waste_generaton_coa_project_linkage_rgpl_source_check CHECK ((rgpl_source = ANY (ARRAY['SITEAA'::text, 'COA'::text])))
);


ALTER TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage OWNER TO postgres;

--
-- TOC entry 16341 (class 0 OID 0)
-- Dependencies: 4539
-- Name: TABLE waste_generaton_coa_project_linkage; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage IS 'Registro de vinculación voluntaria de RG a proyectos por parte del operador';


--
-- TOC entry 16342 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.rgpl_source; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_source IS 'Origen del RG: SITEAA o COA';


--
-- TOC entry 16343 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.hwge_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.hwge_id IS 'ID del RG en SITEAA';


--
-- TOC entry 16344 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.ware_id IS 'ID del RG en COA';


--
-- TOC entry 16345 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.pren_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.pren_id IS 'ID del proyecto en SITEAA';


--
-- TOC entry 16346 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.prco_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.prco_id IS 'ID del proyecto en COA';


--
-- TOC entry 16347 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.rgpl_linkage_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_linkage_date IS 'Fecha en que se realizó la vinculación voluntaria';


--
-- TOC entry 16348 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.rgpl_linked_by; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_linked_by IS 'Usuario que realizó la vinculación';


--
-- TOC entry 16349 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.rgpl_comments; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_comments IS 'Comentarios opcionales del operador sobre la vinculación';


--
-- TOC entry 16350 (class 0 OID 0)
-- Dependencies: 4539
-- Name: COLUMN waste_generaton_coa_project_linkage.rgpl_manual_linkage; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_manual_linkage IS 'TRUE si la vinculación fue voluntaria (no técnica)';


--
-- TOC entry 4540 (class 1259 OID 43687519)
-- Name: waste_generaton_coa_project_linkage_rgpl_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq OWNER TO postgres;

--
-- TOC entry 16352 (class 0 OID 0)
-- Dependencies: 4540
-- Name: waste_generaton_coa_project_linkage_rgpl_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq OWNED BY coa_waste_generator_update.waste_generaton_coa_project_linkage.rgpl_id;


--
-- TOC entry 4541 (class 1259 OID 43687521)
-- Name: waste_generaton_coa_validation; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generaton_coa_validation (
    rgva_id integer NOT NULL,
    rgva_source text NOT NULL,
    hwge_id integer,
    ware_id integer,
    rgva_validation_result boolean NOT NULL,
    rgva_validation_date timestamp without time zone DEFAULT now() NOT NULL,
    rgva_validator_user character varying(255) NOT NULL,
    rgva_project_linked boolean NOT NULL,
    pren_id integer,
    prco_id integer,
    rgva_extended_responsibility boolean NOT NULL,
    rgva_comments text,
    CONSTRAINT chk_rgva_source_consistency CHECK ((((rgva_source = 'SITEAA'::text) AND (hwge_id IS NOT NULL) AND (ware_id IS NULL) AND (pren_id IS NOT NULL) AND (prco_id IS NULL)) OR ((rgva_source = 'COA'::text) AND (ware_id IS NOT NULL) AND (hwge_id IS NULL) AND (prco_id IS NOT NULL) AND (pren_id IS NULL)))),
    CONSTRAINT waste_generaton_coa_validation_rgva_source_check CHECK ((rgva_source = ANY (ARRAY['SITEAA'::text, 'COA'::text])))
);


ALTER TABLE coa_waste_generator_update.waste_generaton_coa_validation OWNER TO postgres;

--
-- TOC entry 16354 (class 0 OID 0)
-- Dependencies: 4541
-- Name: TABLE waste_generaton_coa_validation; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation IS 'Registro de validaciones técnicas de RG, vinculadas a proyectos SITEAA o COA';


--
-- TOC entry 16355 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_source; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_source IS 'Origen del RG: SITEAA o COA';


--
-- TOC entry 16356 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.hwge_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.hwge_id IS 'ID del RG en SITEAA';


--
-- TOC entry 16357 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.ware_id IS 'ID del RG en COA';


--
-- TOC entry 16358 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_validation_result; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_validation_result IS 'Resultado de validación: TRUE si válido, FALSE si inválido';


--
-- TOC entry 16359 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_validation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_validation_date IS 'Fecha en que se realizó la validación';


--
-- TOC entry 16360 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_validator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_validator_user IS 'Usuario técnico que realizó la validación';


--
-- TOC entry 16361 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_project_linked; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_project_linked IS 'TRUE si el RG está vinculado a un proyecto';


--
-- TOC entry 16362 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.pren_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.pren_id IS 'ID del proyecto en SITEAA';


--
-- TOC entry 16363 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.prco_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.prco_id IS 'ID del proyecto en COA';


--
-- TOC entry 16364 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_extended_responsibility; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_extended_responsibility IS 'TRUE si el RG tiene responsabilidad extendida';


--
-- TOC entry 16365 (class 0 OID 0)
-- Dependencies: 4541
-- Name: COLUMN waste_generaton_coa_validation.rgva_comments; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation.rgva_comments IS 'Comentarios generales del validador sobre el proceso';


--
-- TOC entry 4542 (class 1259 OID 43687530)
-- Name: waste_generaton_coa_validation_observation; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation (
    rgvo_id integer NOT NULL,
    rgva_id integer NOT NULL,
    rgvo_observation_type character varying(100) NOT NULL,
    rgvo_observation_text text NOT NULL,
    rgvo_created_at timestamp without time zone DEFAULT now() NOT NULL,
    rgvo_created_by character varying(255) NOT NULL
);


ALTER TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation OWNER TO postgres;

--
-- TOC entry 16367 (class 0 OID 0)
-- Dependencies: 4542
-- Name: TABLE waste_generaton_coa_validation_observation; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation IS 'Observaciones registradas cuando una validación de RG resulta negativa';


--
-- TOC entry 16368 (class 0 OID 0)
-- Dependencies: 4542
-- Name: COLUMN waste_generaton_coa_validation_observation.rgva_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation_observation.rgva_id IS 'ID de la validación a la que pertenece la observación';


--
-- TOC entry 16369 (class 0 OID 0)
-- Dependencies: 4542
-- Name: COLUMN waste_generaton_coa_validation_observation.rgvo_observation_type; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation_observation.rgvo_observation_type IS 'Tipo de observación: Ej. coordenadas inválidas, documento faltante';


--
-- TOC entry 16370 (class 0 OID 0)
-- Dependencies: 4542
-- Name: COLUMN waste_generaton_coa_validation_observation.rgvo_observation_text; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation_observation.rgvo_observation_text IS 'Detalle textual de la observación registrada';


--
-- TOC entry 16371 (class 0 OID 0)
-- Dependencies: 4542
-- Name: COLUMN waste_generaton_coa_validation_observation.rgvo_created_at; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation_observation.rgvo_created_at IS 'Fecha en que se registró la observación';


--
-- TOC entry 16372 (class 0 OID 0)
-- Dependencies: 4542
-- Name: COLUMN waste_generaton_coa_validation_observation.rgvo_created_by; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generaton_coa_validation_observation.rgvo_created_by IS 'Usuario que registró la observación';


--
-- TOC entry 4543 (class 1259 OID 43687537)
-- Name: waste_generaton_coa_validation_observation_rgvo_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq OWNER TO postgres;

--
-- TOC entry 16374 (class 0 OID 0)
-- Dependencies: 4543
-- Name: waste_generaton_coa_validation_observation_rgvo_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq OWNED BY coa_waste_generator_update.waste_generaton_coa_validation_observation.rgvo_id;


--
-- TOC entry 4544 (class 1259 OID 43687539)
-- Name: waste_generaton_coa_validation_rgva_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq OWNER TO postgres;

--
-- TOC entry 16376 (class 0 OID 0)
-- Dependencies: 4544
-- Name: waste_generaton_coa_validation_rgva_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq OWNED BY coa_waste_generator_update.waste_generaton_coa_validation.rgva_id;


--
-- TOC entry 4545 (class 1259 OID 43687561)
-- Name: waste_generator_record_coa_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generator_record_coa_update (
    ware_id integer NOT NULL,
    ware_code character varying(255) NOT NULL,
    ware_status boolean DEFAULT true NOT NULL,
    user_id integer NOT NULL,
    ware_delete_reason character varying(25000),
    ware_deactivation_date timestamp(6) without time zone,
    wapo_id integer,
    ware_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    ware_creator_user character varying(255),
    ware_date_update timestamp without time zone,
    ware_user_update character varying(255),
    ware_observation_bd character varying(1024),
    ware_responsibility_held boolean,
    ware_finalized boolean DEFAULT false NOT NULL,
    ware_send_date_information timestamp without time zone
);


ALTER TABLE coa_waste_generator_update.waste_generator_record_coa_update OWNER TO postgres;

--
-- TOC entry 16378 (class 0 OID 0)
-- Dependencies: 4545
-- Name: TABLE waste_generator_record_coa_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generator_record_coa_update IS 'Información de Registro Generador de Residuos o Desechos Especiales y/o Peligrosos Información General ';


--
-- TOC entry 16379 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_id IS 'Clave primaria ';


--
-- TOC entry 16380 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_code; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_code IS 'Código del RGD';


--
-- TOC entry 16381 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_status IS 'Estado del registro generador de desechos';


--
-- TOC entry 16382 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.user_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.user_id IS 'Clave foranea de la tabla users';


--
-- TOC entry 16383 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_delete_reason; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_delete_reason IS 'Razon de la desactivación del RGD
';


--
-- TOC entry 16384 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_deactivation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_deactivation_date IS 'Fecha desactivación del RGD';


--
-- TOC entry 16385 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.wapo_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.wapo_id IS 'Clave foranea de la tabla waste_policies_coa';


--
-- TOC entry 16386 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_creation_date IS 'Fecha de creación';


--
-- TOC entry 16387 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_creator_user IS 'Usuario que crea';


--
-- TOC entry 16388 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_date_update IS 'Fecha actualización';


--
-- TOC entry 16389 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16390 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_observation_bd IS 'Campo de observación para base de datos';


--
-- TOC entry 16391 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_responsibility_held; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_responsibility_held IS 'Responsabilidad extendida';


--
-- TOC entry 16392 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_finalized; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_finalized IS 'Si esta finalizado';


--
-- TOC entry 16393 (class 0 OID 0)
-- Dependencies: 4545
-- Name: COLUMN waste_generator_record_coa_update.ware_send_date_information; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_coa_update.ware_send_date_information IS 'fecha envio informacion';


--
-- TOC entry 4546 (class 1259 OID 43687570)
-- Name: waste_generator_record_document_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generator_record_document_update (
    wgrd_id integer NOT NULL,
    ware_id integer,
    wgrd_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    wgrd_creator_user character varying(256),
    wgrd_date_update timestamp without time zone,
    wgrd_user_update character varying(256),
    wgrd_observation_bd character varying(1024),
    wgrd_document_number character varying,
    wgrd_date_docuement_number timestamp without time zone,
    wgrd_status boolean DEFAULT true NOT NULL,
    wgrd_is_final boolean
);


ALTER TABLE coa_waste_generator_update.waste_generator_record_document_update OWNER TO postgres;

--
-- TOC entry 16395 (class 0 OID 0)
-- Dependencies: 4546
-- Name: TABLE waste_generator_record_document_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generator_record_document_update IS 'Documento del registro generador de desechos
';


--
-- TOC entry 16396 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_id IS 'Id de la tabla';


--
-- TOC entry 16397 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_creation_date IS 'Fecha de creacion registro';


--
-- TOC entry 16398 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_creator_user IS 'Usuario que crea el registro';


--
-- TOC entry 16399 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_date_update IS 'Fecha de Actualización del registro';


--
-- TOC entry 16400 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_user_update IS 'Usuario que modifica el registro';


--
-- TOC entry 16401 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_observation_bd IS 'Observación para base de datos';


--
-- TOC entry 16402 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_document_number; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_document_number IS 'numero del documento';


--
-- TOC entry 16403 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_date_docuement_number; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_date_docuement_number IS 'Fecha creacion del numero documento';


--
-- TOC entry 16404 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_status IS 'Estado del Registro';


--
-- TOC entry 16405 (class 0 OID 0)
-- Dependencies: 4546
-- Name: COLUMN waste_generator_record_document_update.wgrd_is_final; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_document_update.wgrd_is_final IS 'Indica si es un registro final generado al obtener la resolucion';


--
-- TOC entry 4547 (class 1259 OID 43687578)
-- Name: waste_generator_record_document_wgrd_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq OWNER TO postgres;

--
-- TOC entry 16407 (class 0 OID 0)
-- Dependencies: 4547
-- Name: waste_generator_record_document_wgrd_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq OWNED BY coa_waste_generator_update.waste_generator_record_document_update.wgrd_id;


--
-- TOC entry 4548 (class 1259 OID 43687580)
-- Name: waste_generator_record_office_pronouncement_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update (
    wgro_id integer NOT NULL,
    ware_id integer,
    wgro_document_number character varying(1024),
    wgro_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    wgro_creator_user character varying(1024),
    wgro_date_update timestamp without time zone,
    wgro_user_update character varying,
    wgro_observation_bd character varying(1024),
    wgro_date_document_number timestamp without time zone,
    wgro_status boolean DEFAULT true NOT NULL
);


ALTER TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update OWNER TO postgres;

--
-- TOC entry 16409 (class 0 OID 0)
-- Dependencies: 4548
-- Name: TABLE waste_generator_record_office_pronouncement_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update IS 'Oficio de pronunciamiento del RGD';


--
-- TOC entry 16410 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_id IS 'Identificador de la tabla';


--
-- TOC entry 16411 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.ware_id IS 'Clave foranea de la tabla rgd';


--
-- TOC entry 16412 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_document_number; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_document_number IS 'Numero del documento';


--
-- TOC entry 16413 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_creation_date IS 'Fecha de creacion del registro';


--
-- TOC entry 16414 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_date_update IS 'Fecha de modificacion del registro';


--
-- TOC entry 16415 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_user_update IS 'Usuario que actualiza el registro';


--
-- TOC entry 16416 (class 0 OID 0)
-- Dependencies: 4548
-- Name: COLUMN waste_generator_record_office_pronouncement_update.wgro_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_observation_bd IS 'Observación para base de datos';


--
-- TOC entry 4549 (class 1259 OID 43687588)
-- Name: waste_generator_record_office_pronouncement_wgro_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq OWNER TO postgres;

--
-- TOC entry 16418 (class 0 OID 0)
-- Dependencies: 4549
-- Name: waste_generator_record_office_pronouncement_wgro_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq OWNED BY coa_waste_generator_update.waste_generator_record_office_pronouncement_update.wgro_id;


--
-- TOC entry 4550 (class 1259 OID 43687590)
-- Name: waste_generator_record_project_licencing_coa_update; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_generator_record_project_licencing_coa_update (
    wapr_id integer NOT NULL,
    ware_id integer,
    prco_id integer,
    wapr_status boolean DEFAULT true,
    wapr_come_from character varying(1024),
    wapr_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    wapr_creator_user character varying(1024),
    wapr_date_update timestamp without time zone,
    wapr_user_update character varying(1024),
    wapr_observation_bd character varying(1024),
    id_proyect integer,
    wapr_description_system character varying(1024),
    wapr_4cat_sect character varying(30),
    enaa_id integer,
    wapr_id_history integer,
    wapr_date_unbind timestamp without time zone
);


ALTER TABLE coa_waste_generator_update.waste_generator_record_project_licencing_coa_update OWNER TO postgres;

--
-- TOC entry 16420 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_id IS 'Clave primaria';


--
-- TOC entry 16421 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.ware_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.ware_id IS 'Clave foranea de coa_waste_generator_update.waste_generator_record_coa';


--
-- TOC entry 16422 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.prco_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.prco_id IS 'clave foranea de la tabla coa_mae.project_licencing_coa';


--
-- TOC entry 16423 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_status IS 'Estado del registro';


--
-- TOC entry 16424 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_come_from; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_come_from IS 'Emision del proyecto';


--
-- TOC entry 16425 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_creation_date IS 'Fecha Creación';


--
-- TOC entry 16426 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_creator_user IS 'Usuario que crea';


--
-- TOC entry 16427 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_date_update IS 'Fecha de Actualización';


--
-- TOC entry 16428 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16429 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_observation_bd IS 'Observación para base de datos';


--
-- TOC entry 16430 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.id_proyect; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.id_proyect IS 'Identificador de los proyectos antiguos';


--
-- TOC entry 16431 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_description_system; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_description_system IS 'Nombre del Sistema Antiguo';


--
-- TOC entry 16432 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_4cat_sect; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_4cat_sect IS 'Campo que almacena el codigo del proyectos de los sistemas de cuatro categorias y sector subsector.';


--
-- TOC entry 16433 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.enaa_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.enaa_id IS 'fk, Clave foranea de la tabla principal del esquema de digitalización';


--
-- TOC entry 16434 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_id_history; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_id_history IS 'Fk, de la tabla coa_waste_generator_update.waste_generator_record_project_licencing_coa, que identifica el respaldo cuando se ha desvinculado el rgd';


--
-- TOC entry 16435 (class 0 OID 0)
-- Dependencies: 4550
-- Name: COLUMN waste_generator_record_project_licencing_coa_update.wapr_date_unbind; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_date_unbind IS 'Fecha en la que se desvinculo el rgd del proyecto asociado.';


--
-- TOC entry 4551 (class 1259 OID 43687598)
-- Name: waste_generator_record_project_licencing_coa_wapr_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq OWNER TO postgres;

--
-- TOC entry 16437 (class 0 OID 0)
-- Dependencies: 4551
-- Name: waste_generator_record_project_licencing_coa_wapr_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq OWNED BY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update.wapr_id;


--
-- TOC entry 4552 (class 1259 OID 43687600)
-- Name: waste_generator_record_ware_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_generator_record_ware_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_ware_id_seq OWNER TO postgres;

--
-- TOC entry 16439 (class 0 OID 0)
-- Dependencies: 4552
-- Name: waste_generator_record_ware_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_generator_record_ware_id_seq OWNED BY coa_waste_generator_update.waste_generator_record_coa_update.ware_id;


--
-- TOC entry 4553 (class 1259 OID 43687630)
-- Name: waste_waste_generation_points; Type: TABLE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TABLE coa_waste_generator_update.waste_waste_generation_points (
    wwgp_id integer NOT NULL,
    wwgp_status boolean DEFAULT true NOT NULL,
    wada_id integer NOT NULL,
    wwgp_generate_waste boolean DEFAULT false NOT NULL,
    wwgp_quantity_tons numeric,
    wwgp_quantity_kilograms numeric,
    wwgp_creation_date timestamp without time zone DEFAULT now() NOT NULL,
    wwgp_creator_user character varying(255),
    wwgp_date_update timestamp without time zone,
    wwgp_user_update character varying(255),
    wwgp_observation_bd character varying(1024),
    wwgp_internal_management boolean,
    wwgp_other character varying(1024),
    ware_id integer,
    wwgp_search_added boolean DEFAULT false NOT NULL,
    wwgp_waste_description character varying(1024),
    wwgp_quantity_unit numeric,
    wwgp_management_individual boolean,
    wwgp_management_system_name character varying(256),
    wwgp_management_system_date timestamp without time zone
);


ALTER TABLE coa_waste_generator_update.waste_waste_generation_points OWNER TO postgres;

--
-- TOC entry 16441 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_id IS 'Clave primaria';


--
-- TOC entry 16442 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_status; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_status IS 'Estado del registro';


--
-- TOC entry 16443 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wada_id; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wada_id IS 'Clave foranea de la tabla suia_iii.waste_dangerous';


--
-- TOC entry 16444 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_generate_waste; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_generate_waste IS 'Genera desecho
false si genera
true no genera';


--
-- TOC entry 16445 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_quantity_tons; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_quantity_tons IS 'Cantidad en toneladas';


--
-- TOC entry 16446 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_quantity_kilograms; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_quantity_kilograms IS 'Cantidad en Kilogramos';


--
-- TOC entry 16447 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_creation_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_creation_date IS 'Fecha creación';


--
-- TOC entry 16448 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_creator_user; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_creator_user IS 'Usuario crea';


--
-- TOC entry 16449 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_date_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_date_update IS 'Fecha actualización';


--
-- TOC entry 16450 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_user_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_user_update IS 'Usuario que actualiza';


--
-- TOC entry 16451 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_observation_bd; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_observation_bd IS 'Observación campo para base datos';


--
-- TOC entry 16452 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_internal_management; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_internal_management IS 'Gestion Interna del residuo';


--
-- TOC entry 16453 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_other; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_other IS 'Otra';


--
-- TOC entry 16454 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_search_added; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_search_added IS 'Desecho es de busqueda o agregado';


--
-- TOC entry 16455 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_waste_description; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_waste_description IS 'Descripcion del desecho';


--
-- TOC entry 16456 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_quantity_unit; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_quantity_unit IS 'Cantidad en unidades';


--
-- TOC entry 16457 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_management_individual; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_management_individual IS 'true si el sistema de gestion es individual, false si el sistema de gestion es colectiva ';


--
-- TOC entry 16458 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_management_system_name; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_management_system_name IS 'Nombre del sistema colectivo';


--
-- TOC entry 16459 (class 0 OID 0)
-- Dependencies: 4553
-- Name: COLUMN waste_waste_generation_points.wwgp_management_system_date; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON COLUMN coa_waste_generator_update.waste_waste_generation_points.wwgp_management_system_date IS 'fecha de adhesión al sistema colectivo';


--
-- TOC entry 4554 (class 1259 OID 43687640)
-- Name: waste_waste_generation_points_wwgp_id_seq; Type: SEQUENCE; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE SEQUENCE coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq OWNER TO postgres;

--
-- TOC entry 16461 (class 0 OID 0)
-- Dependencies: 4554
-- Name: waste_waste_generation_points_wwgp_id_seq; Type: SEQUENCE OWNED BY; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER SEQUENCE coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq OWNED BY coa_waste_generator_update.waste_waste_generation_points.wwgp_id;


--
-- TOC entry 15864 (class 2604 OID 43687642)
-- Name: coordinates_coa_update coor_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.coordinates_coa_update ALTER COLUMN coor_id SET DEFAULT nextval('coa_waste_generator_update.coordinates_coa_update_coor_id_seq'::regclass);


--
-- TOC entry 15868 (class 2604 OID 43687643)
-- Name: documents_coa_waste_generator_update dowa_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.documents_coa_waste_generator_update ALTER COLUMN dowa_id SET DEFAULT nextval('coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq'::regclass);


--
-- TOC entry 15871 (class 2604 OID 43687645)
-- Name: generation_points_waste_update gewa_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.generation_points_waste_update ALTER COLUMN gewa_id SET DEFAULT nextval('coa_waste_generator_update.generation_points_waste_update_gewa_id_seq'::regclass);


--
-- TOC entry 15874 (class 2604 OID 43687646)
-- Name: recovery_point_shapes_coa_update rpsh_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_point_shapes_coa_update ALTER COLUMN rpsh_id SET DEFAULT nextval('coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq'::regclass);


--
-- TOC entry 15877 (class 2604 OID 43687647)
-- Name: recovery_points_coa_update repo_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_points_coa_update ALTER COLUMN repo_id SET DEFAULT nextval('coa_waste_generator_update.recovery_points_coa_update_repo_id_seq'::regclass);


--
-- TOC entry 15880 (class 2604 OID 43687648)
-- Name: waste_generaton_coa_project_linkage rgpl_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_project_linkage ALTER COLUMN rgpl_id SET DEFAULT nextval('coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq'::regclass);


--
-- TOC entry 15883 (class 2604 OID 43687649)
-- Name: waste_generaton_coa_validation rgva_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_validation ALTER COLUMN rgva_id SET DEFAULT nextval('coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq'::regclass);


--
-- TOC entry 15885 (class 2604 OID 43687650)
-- Name: waste_generaton_coa_validation_observation rgvo_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_validation_observation ALTER COLUMN rgvo_id SET DEFAULT nextval('coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq'::regclass);


--
-- TOC entry 15887 (class 2604 OID 43687653)
-- Name: waste_generator_record_coa_update ware_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_coa_update ALTER COLUMN ware_id SET DEFAULT nextval('coa_waste_generator_update.waste_generator_record_ware_id_seq'::regclass);


--
-- TOC entry 15891 (class 2604 OID 43687654)
-- Name: waste_generator_record_document_update wgrd_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_document_update ALTER COLUMN wgrd_id SET DEFAULT nextval('coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq'::regclass);


--
-- TOC entry 15894 (class 2604 OID 43687655)
-- Name: waste_generator_record_office_pronouncement_update wgro_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_office_pronouncement_update ALTER COLUMN wgro_id SET DEFAULT nextval('coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq'::regclass);


--
-- TOC entry 15897 (class 2604 OID 43687656)
-- Name: waste_generator_record_project_licencing_coa_update wapr_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update ALTER COLUMN wapr_id SET DEFAULT nextval('coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq'::regclass);


--
-- TOC entry 15900 (class 2604 OID 43687660)
-- Name: waste_waste_generation_points wwgp_id; Type: DEFAULT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_waste_generation_points ALTER COLUMN wwgp_id SET DEFAULT nextval('coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq'::regclass);


--
-- TOC entry 16237 (class 0 OID 43687448)
-- Dependencies: 4529
-- Data for Name: coordinates_coa_update; Type: TABLE DATA; Schema: coa_waste_generator_update; Owner: postgres
--


--
-- TOC entry 16463 (class 0 OID 0)
-- Dependencies: 4530
-- Name: coordinates_coa_update_coor_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.coordinates_coa_update_coor_id_seq', 1, false);


--
-- TOC entry 16464 (class 0 OID 0)
-- Dependencies: 4532
-- Name: documents_coa_waste_generator_update_dowa_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq', 1, false);


--
-- TOC entry 16465 (class 0 OID 0)
-- Dependencies: 4534
-- Name: generation_points_waste_update_gewa_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.generation_points_waste_update_gewa_id_seq', 1, false);


--
-- TOC entry 16466 (class 0 OID 0)
-- Dependencies: 4536
-- Name: recovery_point_shapes_coa_update_rpsh_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq', 1, false);


--
-- TOC entry 16467 (class 0 OID 0)
-- Dependencies: 4538
-- Name: recovery_points_coa_update_repo_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.recovery_points_coa_update_repo_id_seq', 1, false);


--
-- TOC entry 16468 (class 0 OID 0)
-- Dependencies: 4540
-- Name: waste_generaton_coa_project_linkage_rgpl_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq', 1, false);


--
-- TOC entry 16469 (class 0 OID 0)
-- Dependencies: 4543
-- Name: waste_generaton_coa_validation_observation_rgvo_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq', 1, false);


--
-- TOC entry 16470 (class 0 OID 0)
-- Dependencies: 4544
-- Name: waste_generaton_coa_validation_rgva_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq', 1, false);


--
-- TOC entry 16471 (class 0 OID 0)
-- Dependencies: 4547
-- Name: waste_generator_record_document_wgrd_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq', 7817, true);


--
-- TOC entry 16472 (class 0 OID 0)
-- Dependencies: 4549
-- Name: waste_generator_record_office_pronouncement_wgro_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq', 7602, true);


--
-- TOC entry 16473 (class 0 OID 0)
-- Dependencies: 4551
-- Name: waste_generator_record_project_licencing_coa_wapr_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq', 11011, true);


--
-- TOC entry 16474 (class 0 OID 0)
-- Dependencies: 4552
-- Name: waste_generator_record_ware_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_generator_record_ware_id_seq', 12849, true);


--
-- TOC entry 16475 (class 0 OID 0)
-- Dependencies: 4554
-- Name: waste_waste_generation_points_wwgp_id_seq; Type: SEQUENCE SET; Schema: coa_waste_generator_update; Owner: postgres
--

SELECT pg_catalog.setval('coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq', 344008, true);


--
-- TOC entry 15910 (class 2606 OID 43687662)
-- Name: coordinates_coa_update coor_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.coordinates_coa_update
    ADD CONSTRAINT coor_id PRIMARY KEY (coor_id);


--
-- TOC entry 15913 (class 2606 OID 43687664)
-- Name: documents_coa_waste_generator_update dowa_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.documents_coa_waste_generator_update
    ADD CONSTRAINT dowa_id PRIMARY KEY (dowa_id);


--
-- TOC entry 15919 (class 2606 OID 43687668)
-- Name: generation_points_waste_update gewa_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.generation_points_waste_update
    ADD CONSTRAINT gewa_id PRIMARY KEY (gewa_id);


--
-- TOC entry 15927 (class 2606 OID 43687670)
-- Name: recovery_points_coa_update repo_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_points_coa_update
    ADD CONSTRAINT repo_id PRIMARY KEY (repo_id);


--
-- TOC entry 15923 (class 2606 OID 43687678)
-- Name: recovery_point_shapes_coa_update rpsh_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_point_shapes_coa_update
    ADD CONSTRAINT rpsh_id PRIMARY KEY (rpsh_id);


--
-- TOC entry 15959 (class 2606 OID 43687686)
-- Name: waste_generator_record_project_licencing_coa_update wapr_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update
    ADD CONSTRAINT wapr_id PRIMARY KEY (wapr_id);


--
-- TOC entry 15949 (class 2606 OID 43687688)
-- Name: waste_generator_record_coa_update ware_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_coa_update
    ADD CONSTRAINT ware_id PRIMARY KEY (ware_id);


--
-- TOC entry 15934 (class 2606 OID 43687672)
-- Name: waste_generaton_coa_project_linkage waste_generaton_coa_project_linkage_pkey; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_project_linkage
    ADD CONSTRAINT waste_generaton_coa_project_linkage_pkey PRIMARY KEY (rgpl_id);


--
-- TOC entry 15945 (class 2606 OID 43687674)
-- Name: waste_generaton_coa_validation_observation waste_generaton_coa_validation_observation_pkey; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_validation_observation
    ADD CONSTRAINT waste_generaton_coa_validation_observation_pkey PRIMARY KEY (rgvo_id);


--
-- TOC entry 15941 (class 2606 OID 43687676)
-- Name: waste_generaton_coa_validation waste_generaton_coa_validation_pkey; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_validation
    ADD CONSTRAINT waste_generaton_coa_validation_pkey PRIMARY KEY (rgva_id);


--
-- TOC entry 15952 (class 2606 OID 43687692)
-- Name: waste_generator_record_document_update wgrd_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_document_update
    ADD CONSTRAINT wgrd_id PRIMARY KEY (wgrd_id);


--
-- TOC entry 15955 (class 2606 OID 43687694)
-- Name: waste_generator_record_office_pronouncement_update wgro_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_office_pronouncement_update
    ADD CONSTRAINT wgro_id PRIMARY KEY (wgro_id);


--
-- TOC entry 15963 (class 2606 OID 43687696)
-- Name: waste_waste_generation_points wwgp_id; Type: CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_waste_generation_points
    ADD CONSTRAINT wwgp_id PRIMARY KEY (wwgp_id);


--
-- TOC entry 15914 (class 1259 OID 43687699)
-- Name: fki_doty_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_doty_id ON coa_waste_generator_update.documents_coa_waste_generator_update USING btree (doty_id);


--
-- TOC entry 15924 (class 1259 OID 43687700)
-- Name: fki_gelo_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_gelo_id ON coa_waste_generator_update.recovery_points_coa_update USING btree (gelo_id);


--
-- TOC entry 15916 (class 1259 OID 43687701)
-- Name: fki_gepo_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_gepo_id ON coa_waste_generator_update.generation_points_waste_update USING btree (gepo_id);


--
-- TOC entry 15956 (class 1259 OID 43687702)
-- Name: fki_prco_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_prco_id ON coa_waste_generator_update.waste_generator_record_project_licencing_coa_update USING btree (prco_id);


--
-- TOC entry 15920 (class 1259 OID 43687703)
-- Name: fki_repo_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_repo_id ON coa_waste_generator_update.recovery_point_shapes_coa_update USING btree (repo_id);


--
-- TOC entry 15911 (class 1259 OID 43687704)
-- Name: fki_rpsh_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_rpsh_id ON coa_waste_generator_update.coordinates_coa_update USING btree (rpsh_id);


--
-- TOC entry 15921 (class 1259 OID 43687705)
-- Name: fki_shty_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_shty_id ON coa_waste_generator_update.recovery_point_shapes_coa_update USING btree (shty_id);


--
-- TOC entry 15946 (class 1259 OID 43687706)
-- Name: fki_user_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_user_id ON coa_waste_generator_update.waste_generator_record_coa_update USING btree (user_id);


--
-- TOC entry 15960 (class 1259 OID 43687708)
-- Name: fki_wada_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_wada_id ON coa_waste_generator_update.waste_waste_generation_points USING btree (wada_id);


--
-- TOC entry 15947 (class 1259 OID 43687710)
-- Name: fki_wapo_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_wapo_id ON coa_waste_generator_update.waste_generator_record_coa_update USING btree (wapo_id);


--
-- TOC entry 15915 (class 1259 OID 43687712)
-- Name: fki_ware__id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_ware__id ON coa_waste_generator_update.documents_coa_waste_generator_update USING btree (ware_id);


--
-- TOC entry 15961 (class 1259 OID 43687713)
-- Name: fki_ware_iId; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX "fki_ware_iId" ON coa_waste_generator_update.waste_waste_generation_points USING btree (ware_id);


--
-- TOC entry 15925 (class 1259 OID 43687714)
-- Name: fki_ware_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_ware_id ON coa_waste_generator_update.recovery_points_coa_update USING btree (ware_id);


--
-- TOC entry 15957 (class 1259 OID 43687715)
-- Name: fki_ware_id_; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_ware_id_ ON coa_waste_generator_update.waste_generator_record_project_licencing_coa_update USING btree (ware_id);


--
-- TOC entry 15950 (class 1259 OID 43687716)
-- Name: fki_ware_iid; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_ware_iid ON coa_waste_generator_update.waste_generator_record_document_update USING btree (ware_id);


--
-- TOC entry 15953 (class 1259 OID 43687717)
-- Name: fki_ware_iidd; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_ware_iidd ON coa_waste_generator_update.waste_generator_record_office_pronouncement_update USING btree (ware_id);


--
-- TOC entry 15917 (class 1259 OID 43687718)
-- Name: fki_wwgp_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX fki_wwgp_id ON coa_waste_generator_update.generation_points_waste_update USING btree (wwgp_id);


--
-- TOC entry 15928 (class 1259 OID 43687724)
-- Name: idx_rgpl_hwge_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgpl_hwge_id ON coa_waste_generator_update.waste_generaton_coa_project_linkage USING btree (hwge_id);


--
-- TOC entry 15929 (class 1259 OID 43687725)
-- Name: idx_rgpl_linked_by; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgpl_linked_by ON coa_waste_generator_update.waste_generaton_coa_project_linkage USING btree (rgpl_linked_by);


--
-- TOC entry 15930 (class 1259 OID 43687726)
-- Name: idx_rgpl_prco_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgpl_prco_id ON coa_waste_generator_update.waste_generaton_coa_project_linkage USING btree (prco_id);


--
-- TOC entry 15931 (class 1259 OID 43687727)
-- Name: idx_rgpl_pren_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgpl_pren_id ON coa_waste_generator_update.waste_generaton_coa_project_linkage USING btree (pren_id);


--
-- TOC entry 15932 (class 1259 OID 43687728)
-- Name: idx_rgpl_ware_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgpl_ware_id ON coa_waste_generator_update.waste_generaton_coa_project_linkage USING btree (ware_id);


--
-- TOC entry 15942 (class 1259 OID 43687729)
-- Name: idx_rgvo_created_by; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgvo_created_by ON coa_waste_generator_update.waste_generaton_coa_validation_observation USING btree (rgvo_created_by);


--
-- TOC entry 15943 (class 1259 OID 43687730)
-- Name: idx_rgvo_rgva_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_rgvo_rgva_id ON coa_waste_generator_update.waste_generaton_coa_validation_observation USING btree (rgva_id);


--
-- TOC entry 15935 (class 1259 OID 43687719)
-- Name: idx_waste_generaton_coa_validation_hwge_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_waste_generaton_coa_validation_hwge_id ON coa_waste_generator_update.waste_generaton_coa_validation USING btree (hwge_id);


--
-- TOC entry 15936 (class 1259 OID 43687720)
-- Name: idx_waste_generaton_coa_validation_prco_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_waste_generaton_coa_validation_prco_id ON coa_waste_generator_update.waste_generaton_coa_validation USING btree (prco_id);


--
-- TOC entry 15937 (class 1259 OID 43687721)
-- Name: idx_waste_generaton_coa_validation_pren_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_waste_generaton_coa_validation_pren_id ON coa_waste_generator_update.waste_generaton_coa_validation USING btree (pren_id);


--
-- TOC entry 15938 (class 1259 OID 43687722)
-- Name: idx_waste_generaton_coa_validation_result; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_waste_generaton_coa_validation_result ON coa_waste_generator_update.waste_generaton_coa_validation USING btree (rgva_validation_result);


--
-- TOC entry 15939 (class 1259 OID 43687723)
-- Name: idx_waste_generaton_coa_validation_ware_id; Type: INDEX; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE INDEX idx_waste_generaton_coa_validation_ware_id ON coa_waste_generator_update.waste_generaton_coa_validation USING btree (ware_id);


--
-- TOC entry 15983 (class 2620 OID 43687731)
-- Name: waste_generator_record_project_licencing_coa_update tg_auditar; Type: TRIGGER; Schema: coa_waste_generator_update; Owner: postgres
--

CREATE TRIGGER tg_auditar AFTER INSERT OR DELETE OR UPDATE ON coa_waste_generator_update.waste_generator_record_project_licencing_coa_update FOR EACH ROW EXECUTE PROCEDURE audit.if_modified_func();


--
-- TOC entry 15978 (class 2606 OID 43687742)
-- Name: waste_generator_record_project_licencing_coa_update fk_enaa_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update
    ADD CONSTRAINT fk_enaa_id FOREIGN KEY (enaa_id) REFERENCES coa_digitalization_linkage.environmental_administrative_authorizations(enaa_id);


--
-- TOC entry 15970 (class 2606 OID 43688312)
-- Name: recovery_points_coa_update fk_gepo_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_points_coa_update
    ADD CONSTRAINT fk_gepo_id FOREIGN KEY (gepo_id) REFERENCES coa_waste_generator_record.generation_points_coa(gepo_id);


--
-- TOC entry 15968 (class 2606 OID 43687752)
-- Name: recovery_point_shapes_coa_update fk_repo_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_point_shapes_coa_update
    ADD CONSTRAINT fk_repo_id FOREIGN KEY (repo_id) REFERENCES coa_waste_generator_update.recovery_points_coa_update(repo_id);


--
-- TOC entry 15971 (class 2606 OID 43687757)
-- Name: recovery_points_coa_update gelo_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_points_coa_update
    ADD CONSTRAINT gelo_id FOREIGN KEY (gelo_id) REFERENCES public.geographical_locations(gelo_id);


--
-- TOC entry 15966 (class 2606 OID 43688183)
-- Name: generation_points_waste_update gepo_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.generation_points_waste_update
    ADD CONSTRAINT gepo_id FOREIGN KEY (gepo_id) REFERENCES coa_waste_generator_record.generation_points_coa(gepo_id);


--
-- TOC entry 15979 (class 2606 OID 43687767)
-- Name: waste_generator_record_project_licencing_coa_update prco_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update
    ADD CONSTRAINT prco_id FOREIGN KEY (prco_id) REFERENCES coa_mae.project_licencing_coa(prco_id);


--
-- TOC entry 15964 (class 2606 OID 43687777)
-- Name: coordinates_coa_update rpsh_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.coordinates_coa_update
    ADD CONSTRAINT rpsh_id FOREIGN KEY (rpsh_id) REFERENCES coa_waste_generator_update.recovery_point_shapes_coa_update(rpsh_id);


--
-- TOC entry 15969 (class 2606 OID 43687782)
-- Name: recovery_point_shapes_coa_update shty_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_point_shapes_coa_update
    ADD CONSTRAINT shty_id FOREIGN KEY (shty_id) REFERENCES suia_iii.shape_types(shty_id);


--
-- TOC entry 15974 (class 2606 OID 43687787)
-- Name: waste_generator_record_coa_update user_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_coa_update
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 15981 (class 2606 OID 43687797)
-- Name: waste_waste_generation_points wada_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_waste_generation_points
    ADD CONSTRAINT wada_id FOREIGN KEY (wada_id) REFERENCES suia_iii.waste_dangerous(wada_id);


--
-- TOC entry 15965 (class 2606 OID 43687817)
-- Name: documents_coa_waste_generator_update ware__id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.documents_coa_waste_generator_update
    ADD CONSTRAINT ware__id FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 15972 (class 2606 OID 43687822)
-- Name: recovery_points_coa_update ware_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.recovery_points_coa_update
    ADD CONSTRAINT ware_id FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 15980 (class 2606 OID 43687827)
-- Name: waste_generator_record_project_licencing_coa_update ware_id_; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_project_licencing_coa_update
    ADD CONSTRAINT ware_id_ FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 15982 (class 2606 OID 43687832)
-- Name: waste_waste_generation_points ware_idd; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_waste_generation_points
    ADD CONSTRAINT ware_idd FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 15976 (class 2606 OID 43687837)
-- Name: waste_generator_record_document_update ware_iid; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_document_update
    ADD CONSTRAINT ware_iid FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 16476 (class 0 OID 0)
-- Dependencies: 15976
-- Name: CONSTRAINT ware_iid ON waste_generator_record_document_update; Type: COMMENT; Schema: coa_waste_generator_update; Owner: postgres
--

COMMENT ON CONSTRAINT ware_iid ON coa_waste_generator_update.waste_generator_record_document_update IS 'clave foranea rgd';


--
-- TOC entry 15977 (class 2606 OID 43687842)
-- Name: waste_generator_record_office_pronouncement_update ware_iidd; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_office_pronouncement_update
    ADD CONSTRAINT ware_iidd FOREIGN KEY (ware_id) REFERENCES coa_waste_generator_update.waste_generator_record_coa_update(ware_id);


--
-- TOC entry 15973 (class 2606 OID 43687772)
-- Name: waste_generaton_coa_validation_observation waste_generaton_coa_validation_observation_rgva_id_fkey; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generaton_coa_validation_observation
    ADD CONSTRAINT waste_generaton_coa_validation_observation_rgva_id_fkey FOREIGN KEY (rgva_id) REFERENCES coa_waste_generator_update.waste_generaton_coa_validation(rgva_id) ON DELETE CASCADE;


--
-- TOC entry 15975 (class 2606 OID 43688373)
-- Name: waste_generator_record_coa_update waste_generator_record_coa_update_waste_policies_coa_fk; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.waste_generator_record_coa_update
    ADD CONSTRAINT waste_generator_record_coa_update_waste_policies_coa_fk FOREIGN KEY (wapo_id) REFERENCES coa_waste_generator_record.waste_policies_coa(wapo_id);


--
-- TOC entry 15967 (class 2606 OID 43687847)
-- Name: generation_points_waste_update wwgp_id; Type: FK CONSTRAINT; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER TABLE ONLY coa_waste_generator_update.generation_points_waste_update
    ADD CONSTRAINT wwgp_id FOREIGN KEY (wwgp_id) REFERENCES coa_waste_generator_update.waste_waste_generation_points(wwgp_id);


--
-- TOC entry 16269 (class 0 OID 0)
-- Dependencies: 347
-- Name: SCHEMA coa_waste_generator_update; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA coa_waste_generator_update TO suia_iii_escritura;
GRANT ALL ON SCHEMA coa_waste_generator_update TO suia_lectura;
GRANT USAGE ON SCHEMA coa_waste_generator_update TO mae_app_user;


--
-- TOC entry 16284 (class 0 OID 0)
-- Dependencies: 4529
-- Name: TABLE coordinates_coa_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.coordinates_coa_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.coordinates_coa_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.coordinates_coa_update TO mae_app_user;


--
-- TOC entry 16286 (class 0 OID 0)
-- Dependencies: 4530
-- Name: SEQUENCE coordinates_coa_update_coor_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.coordinates_coa_update_coor_id_seq TO mae_app_user;


--
-- TOC entry 16300 (class 0 OID 0)
-- Dependencies: 4531
-- Name: TABLE documents_coa_waste_generator_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.documents_coa_waste_generator_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.documents_coa_waste_generator_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.documents_coa_waste_generator_update TO mae_app_user;


--
-- TOC entry 16302 (class 0 OID 0)
-- Dependencies: 4532
-- Name: SEQUENCE documents_coa_waste_generator_update_dowa_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.documents_coa_waste_generator_update_dowa_id_seq TO mae_app_user;


--
-- TOC entry 16307 (class 0 OID 0)
-- Dependencies: 4533
-- Name: TABLE generation_points_waste_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.generation_points_waste_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.generation_points_waste_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.generation_points_waste_update TO mae_app_user;


--
-- TOC entry 16309 (class 0 OID 0)
-- Dependencies: 4534
-- Name: SEQUENCE generation_points_waste_update_gewa_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.generation_points_waste_update_gewa_id_seq TO mae_app_user;


--
-- TOC entry 16319 (class 0 OID 0)
-- Dependencies: 4535
-- Name: TABLE recovery_point_shapes_coa_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.recovery_point_shapes_coa_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.recovery_point_shapes_coa_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.recovery_point_shapes_coa_update TO mae_app_user;


--
-- TOC entry 16321 (class 0 OID 0)
-- Dependencies: 4536
-- Name: SEQUENCE recovery_point_shapes_coa_update_rpsh_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.recovery_point_shapes_coa_update_rpsh_id_seq TO mae_app_user;


--
-- TOC entry 16338 (class 0 OID 0)
-- Dependencies: 4537
-- Name: TABLE recovery_points_coa_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.recovery_points_coa_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.recovery_points_coa_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.recovery_points_coa_update TO mae_app_user;


--
-- TOC entry 16340 (class 0 OID 0)
-- Dependencies: 4538
-- Name: SEQUENCE recovery_points_coa_update_repo_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.recovery_points_coa_update_repo_id_seq TO mae_app_user;


--
-- TOC entry 16351 (class 0 OID 0)
-- Dependencies: 4539
-- Name: TABLE waste_generaton_coa_project_linkage; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage TO read WITH GRANT OPTION;
GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage TO auditoria_lectura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_project_linkage TO mae_app_user;


--
-- TOC entry 16353 (class 0 OID 0)
-- Dependencies: 4540
-- Name: SEQUENCE waste_generaton_coa_project_linkage_rgpl_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generaton_coa_project_linkage_rgpl_id_seq TO mae_app_user;


--
-- TOC entry 16366 (class 0 OID 0)
-- Dependencies: 4541
-- Name: TABLE waste_generaton_coa_validation; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation TO read WITH GRANT OPTION;
GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation TO auditoria_lectura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_validation TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_validation TO mae_app_user;


--
-- TOC entry 16373 (class 0 OID 0)
-- Dependencies: 4542
-- Name: TABLE waste_generaton_coa_validation_observation; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation TO read WITH GRANT OPTION;
GRANT SELECT ON TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation TO auditoria_lectura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generaton_coa_validation_observation TO mae_app_user;


--
-- TOC entry 16375 (class 0 OID 0)
-- Dependencies: 4543
-- Name: SEQUENCE waste_generaton_coa_validation_observation_rgvo_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_observation_rgvo_id_seq TO mae_app_user;


--
-- TOC entry 16377 (class 0 OID 0)
-- Dependencies: 4544
-- Name: SEQUENCE waste_generaton_coa_validation_rgva_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generaton_coa_validation_rgva_id_seq TO mae_app_user;


--
-- TOC entry 16394 (class 0 OID 0)
-- Dependencies: 4545
-- Name: TABLE waste_generator_record_coa_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generator_record_coa_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_coa_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_coa_update TO mae_app_user;


--
-- TOC entry 16406 (class 0 OID 0)
-- Dependencies: 4546
-- Name: TABLE waste_generator_record_document_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generator_record_document_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_document_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_document_update TO mae_app_user;


--
-- TOC entry 16408 (class 0 OID 0)
-- Dependencies: 4547
-- Name: SEQUENCE waste_generator_record_document_wgrd_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generator_record_document_wgrd_id_seq TO mae_app_user;


--
-- TOC entry 16417 (class 0 OID 0)
-- Dependencies: 4548
-- Name: TABLE waste_generator_record_office_pronouncement_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_office_pronouncement_update TO mae_app_user;


--
-- TOC entry 16419 (class 0 OID 0)
-- Dependencies: 4549
-- Name: SEQUENCE waste_generator_record_office_pronouncement_wgro_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generator_record_office_pronouncement_wgro_id_seq TO mae_app_user;


--
-- TOC entry 16436 (class 0 OID 0)
-- Dependencies: 4550
-- Name: TABLE waste_generator_record_project_licencing_coa_update; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_generator_record_project_licencing_coa_update TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_project_licencing_coa_update TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_generator_record_project_licencing_coa_update TO mae_app_user;


--
-- TOC entry 16438 (class 0 OID 0)
-- Dependencies: 4551
-- Name: SEQUENCE waste_generator_record_project_licencing_coa_wapr_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generator_record_project_licencing_coa_wapr_id_seq TO mae_app_user;


--
-- TOC entry 16440 (class 0 OID 0)
-- Dependencies: 4552
-- Name: SEQUENCE waste_generator_record_ware_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_generator_record_ware_id_seq TO mae_app_user;


--
-- TOC entry 16460 (class 0 OID 0)
-- Dependencies: 4553
-- Name: TABLE waste_waste_generation_points; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT ON TABLE coa_waste_generator_update.waste_waste_generation_points TO read WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_waste_generation_points TO suia_iii_escritura;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE coa_waste_generator_update.waste_waste_generation_points TO mae_app_user;


--
-- TOC entry 16462 (class 0 OID 0)
-- Dependencies: 4554
-- Name: SEQUENCE waste_waste_generation_points_wwgp_id_seq; Type: ACL; Schema: coa_waste_generator_update; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE coa_waste_generator_update.waste_waste_generation_points_wwgp_id_seq TO mae_app_user;


--
-- TOC entry 14117 (class 826 OID 43687852)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA coa_waste_generator_update GRANT SELECT,USAGE ON SEQUENCES TO mae_app_user;


--
-- TOC entry 14118 (class 826 OID 43687853)
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA coa_waste_generator_update GRANT ALL ON FUNCTIONS TO mae_app_user;


--
-- TOC entry 14119 (class 826 OID 43687854)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: coa_waste_generator_update; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA coa_waste_generator_update GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO mae_app_user;


-- Completed on 2025-10-15 10:36:17

--
-- PostgreSQL database dump complete
--

\unrestrict 6z69kfHsywULYz40w2ZLBQQim0jdqe7GWpgucyaXkzLbTTbgXoCnQcIqxjaAf7Q

