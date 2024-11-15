import re
import sqlite3
import os
import codecs

# Ruta al archivo GeoPackage
db_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path = os.path.join(os.path.dirname(db_path), "migracion_log.txt")

# Función para escribir mensajes en el archivo de log
def log_message(message):
    with codecs.open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

# Verificar tablas existentes en la base de datos
def log_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    log_message("Tablas en la base de datos:")
    for table in tables:
        log_message(f"- {table[0]}")

# Diccionarios con las estructuras actuales y nuevas
modelo_union = {

    "cca_agrupacioninteresados" : """CREATE TABLE cca_agrupacioninteresados (
    T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_agrupacioninteresados_tipo_fkey REFERENCES cca_grupointeresadotipo DEFERRABLE INITIALLY DEFERRED,
    nombre TEXT(40) NULL
	);""",

    "cca_omisiones" : """CREATE TABLE cca_omisiones (
    T_Id INTEGER NOT NULL PRIMARY KEY,
	T_Ili_Tid TEXT(200) NULL,
	numero_predial TEXT(30) NOT NULL,
	numero_predial_anterior TEXT(20) NULL,
	codigo_orip TEXT(3) NULL,
	matricula_inmobiliaria TEXT(80) NULL,
	nupre TEXT(11) NULL,
	area_terreno DOUBLE NULL CONSTRAINT cca_omisiones_area_terreno_check CHECK( area_terreno BETWEEN 0.0 AND 1.0E8),
	area_construccion DOUBLE NULL CONSTRAINT cca_omisiones_area_construccion_check CHECK( area_construccion BETWEEN 0.0 AND 1.0E9),
	clase_suelo INTEGER NULL CONSTRAINT cca_omisiones_clase_suelo_fkey REFERENCES cca_clasesuelotipo DEFERRABLE INITIALLY DEFERRED,
	condicion_predio INTEGER NULL CONSTRAINT cca_omisiones_condicion_predio_fkey REFERENCES cca_condicionprediotipo DEFERRABLE INITIALLY DEFERRED,
	destinacion_economica INTEGER NULL CONSTRAINT cca_omisiones_destinacion_economica_fkey REFERENCES cca_destinacioneconomicatipo DEFERRABLE INITIALLY DEFERRED,
    observacion TEXT(255) NULL,
	identificado BOOLEAN NULL,
	propietario TEXT(250) NULL
	);""",

    "cca_fuenteadministrativa" : """CREATE TABLE cca_fuenteadministrativa (
	T_Id INTEGER NOT NULL PRIMARY KEY,
	T_Ili_Tid TEXT(200) NULL,
	tipo INTEGER NOT NULL CONSTRAINT cca_fuenteadministrativa_tipo_fkey REFERENCES cca_fuenteadministrativatipo DEFERRABLE INITIALLY DEFERRED,
	numero_fuente TEXT(150) NULL,
	fecha_documento_fuente DATE NULL,
	ente_emisor TEXT(255) NULL,
	observacion TEXT(250) NULL
	);""",

    "cca_interesado" : """CREATE TABLE cca_interesado (
    T_Id INTEGER NOT NULL PRIMARY KEY,
  	T_Ili_Tid TEXT(200) NULL,
  	tipo INTEGER NOT NULL CONSTRAINT cca_interesado_tipo_fkey REFERENCES cca_interesadotipo DEFERRABLE INITIALLY DEFERRED,
  	tipo_documento INTEGER NOT NULL CONSTRAINT cca_interesado_tipo_documento_fkey REFERENCES cca_interesadodocumentotipo DEFERRABLE INITIALLY DEFERRED,
  	documento_identidad TEXT(50) NULL,
  	primer_nombre TEXT(100) NULL,
  	segundo_nombre TEXT(100) NULL,
  	primer_apellido TEXT(100) NULL,
  	segundo_apellido TEXT(100) NULL,
  	sexo INTEGER NULL CONSTRAINT cca_interesado_sexo_fkey REFERENCES cca_sexotipo DEFERRABLE INITIALLY DEFERRED,
  	grupo_etnico INTEGER NULL CONSTRAINT cca_interesado_grupo_etnico_fkey REFERENCES cca_grupoetnicotipo DEFERRABLE INITIALLY DEFERRED,
  	razon_social TEXT(255) NULL,
  	departamento TEXT(100) NULL,
  	municipio TEXT(100) NULL,
  	direccion_residencia TEXT(255) NULL,
  	telefono TEXT(20) NULL,
  	correo_electronico TEXT(100) NULL,
 	autoriza_notificacion_correo INTEGER NULL CONSTRAINT cca_interesado_autoriza_notificacin_crreo_fkey REFERENCES cca_booleanotipo DEFERRABLE INITIALLY DEFERRED,
  	estado_civil INTEGER NULL CONSTRAINT cca_interesado_estado_civil_fkey REFERENCES cca_estadociviltipo DEFERRABLE INITIALLY DEFERRED,
  	nombre TEXT(255) NULL
	);""",

    "cca_miembros" : """CREATE TABLE "cca_miembros" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"interesado"	REAL,
	"agrupacion"	TEXT,
	"participacion"	TEXT
	);""",

    "cca_predio" : """CREATE TABLE "cca_predio" (
	"T_Id"	INTEGER,
	"T_Ili_Tid"	TEXT,
	"id_operacion"	TEXT,
	"departamento_municipio"	TEXT,
	"clase_suelo_registro"	REAL,
	"categoria_suelo"	TEXT,
	"validacion_datos_localizacion"	TEXT,
	"codigo_homologado"	TEXT,
	"codigo_homologado_fmi"	TEXT,
	"nupre"	TEXT,
	"numero_predial"	TEXT,
	"numero_predial_anterior"	TEXT,
	"validacion_datos_catastrales"	TEXT,
	"tiene_fmi"	REAL,
	"codigo_orip"	TEXT,
	"matricula_inmobiliaria"	TEXT,
	"estado_folio"	TEXT,
	"tiene_area_registral"	REAL,
	"area_registral_m2"	REAL,
	"validacion_datos_registrales"	REAL,
	"condicion_predio"	REAL,
	"total_unidades_privadas"	TEXT,
	"numero_torres"	TEXT,
	"area_total_terreno"	TEXT,
	"area_total_terreno_privada"	TEXT,
	"area_total_terreno_comun"	TEXT,
	"area_total_construida"	TEXT,
	"area_total_construida_privada"	TEXT,
	"area_total_construida_comun"	TEXT,
	"predio_matriz"	TEXT,
	"coeficiente_copropiedad"	TEXT,
	"validacion_condicion_predio"	TEXT,
	"destinacion_economica"	REAL,
	"validacion_destinacion_economica"	TEXT,
	"predio_tipo"	REAL,
	"validacion_tipo_predio"	TEXT,
	"validacion_derechos"	TEXT,
	"resultado_visita"	REAL,
	"otro_cual_resultado_visita"	TEXT,
	"suscribe_acta_colindancia"	REAL,
	"valor_referencia"	TEXT,
	"fecha_visita_predial"	TEXT,
	"tipo_documento_quien_atendio"	REAL,
	"numero_documento_quien_atendio"	TEXT,
	"nombres_apellidos_quien_atendio"	TEXT,
	"celular"	TEXT,
	"correo_electronico"	TEXT,
	"observaciones"	TEXT,
	"despojo_abandono"	REAL,
	"estrato"	REAL,
	"otro_cual_estrato"	TEXT,
	"usuario"	REAL
	);""",

    "cca_ofertasmercadoinmobiliario" : """CREATE TABLE "cca_ofertasmercadoinmobiliario" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"tipo_oferta"	TEXT,
	"valor_pedido"	TEXT,
	"valor_negociado"	TEXT,
	"fecha_captura_oferta"	TEXT,
	"tiempo_oferta_mercado"	TEXT,
	"nombre_oferente"	TEXT,
	"numero_contacto_oferente"	TEXT,
	"predio"	INTEGER
	);""",

    "cca_predio_copropiedad" : """CREATE TABLE "cca_predio_copropiedad" (
	"T_Id"	TEXT,
	"unidad_predial"	TEXT,
	"matriz"	REAL,
	"coeficiente"	TEXT
	);""",

    "cca_predio_informalidad" : """CREATE TABLE "cca_predio_informalidad" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"cca_predio_formal"	TEXT,
	"cca_predio_informal"	REAL
	);""",

    "cca_restriccion" : """CREATE TABLE "cca_restriccion" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"tipo"	TEXT,
	"descripcion"	TEXT,
	"predio"	INTEGER
	);""",

    "cca_derecho" : """CREATE TABLE "cca_derecho" (
	"T_Id"	INTEGER,
	"T_Ili_Tid"	TEXT,
	"tipo"	INTEGER,
	"cuota_participacion"	REAL,
	"fraccion_derecho"	REAL,
	"fecha_inicio_tenencia"	TEXT,
	"origen_derecho"	REAL,
	"observacion"	TEXT,
	"agrupacion_interesados"	TEXT,
	"interesado"	TEXT,
	"predio"	REAL
	);""",

    "cca_fuenteadministrativa_derecho" : """CREATE TABLE "cca_fuenteadministrativa_derecho" (
	"T_Id"	INTEGER,
	"T_Ili_Tid"	TEXT,
	"derecho"	REAL,
	"fuente_administrativa"	REAL
	);""",

    "cca_estructuraamenazariesgovulnerabilidad" : """CREATE TABLE "cca_estructuraamenazariesgovulnerabilidad" (
	"T_Id"	TEXT,
	"T_Seq"	TEXT,
	"tipo_amenaza_riesgo_vulnerabilidad"	TEXT,
	"observacion"	TEXT,
	"cca_predio_amenazariesgovulnerabilidad"	INTEGER
	);""",

    "cca_estructuranovedadfmi" : """CREATE TABLE "cca_estructuranovedadfmi" (
	"T_Id"	TEXT,
	"T_Seq"	TEXT,
	"codigo_orip"	TEXT,
	"numero_fmi"	TEXT,
	"tipo_novedadfmi"	TEXT,
	"cca_predio_novedad_fmi"	REAL
	);""",

    "cca_estructuranovedadnumeropredial" : """CREATE TABLE "cca_estructuranovedadnumeropredial" (
	"T_Id"	INTEGER,
	"T_Seq"	TEXT,
	"numero_predial"	TEXT,
	"tipo_novedad"	INTEGER,
	"cca_predio_novedad_numeros_prediales"	REAL
	);""",

    "cca_usuario" : """CREATE TABLE cca_usuario (
  	T_Id INTEGER NOT NULL PRIMARY KEY,
  	T_Ili_Tid TEXT(200) NULL,
  	id TEXT(20) NULL,
  	tipo_documento INTEGER NOT NULL CONSTRAINT cca_usuario_tipo_documento_fkey REFERENCES cca_interesadodocumentotipo DEFERRABLE INITIALLY DEFERRED,
  	numero_documento TEXT(20) NOT NULL,
  	coordinador TEXT(255) NULL,
	estado INTEGER NULL CONSTRAINT cca_usuario_estado_fkey REFERENCES cca_estadotipo DEFERRABLE INITIALLY DEFERRED,
  	departamento_municipio_codigo TEXT(5) NULL,
  	nombre TEXT(150) NOT NULL,
  	contrasena TEXT(20) NULL,
  	rol INTEGER NOT NULL CONSTRAINT cca_usuario_rol_fkey REFERENCES cca_roltipo DEFERRABLE INITIALLY DEFERRED,
  	"municipio_codigo" TEXT(20)
	);""",

    "cca_caracteristicasunidadconstruccion" : """CREATE TABLE cca_caracteristicasunidadconstruccion (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    identificador TEXT(5) NOT NULL,
    tipo_dominio INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_dominio_fkey REFERENCES cca_dominioconstrucciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_construccion INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_construccion_fkey REFERENCES cca_construcciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_unidad_construccion INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_unidad_construccion_fkey REFERENCES cca_unidadconstrucciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_planta INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_planta_fkey REFERENCES cca_construccionplantatipo DEFERRABLE INITIALLY DEFERRED,
    total_habitaciones INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_habitaciones_check CHECK( total_habitaciones BETWEEN 0 AND 999999),
    total_banios INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_banios_check CHECK( total_banios BETWEEN 0 AND 999999),
    total_locales INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_locales_check CHECK( total_locales BETWEEN 0 AND 999999),
    total_plantas INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_plantas_check CHECK( total_plantas BETWEEN 0 AND 150),
    uso INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_uso_fkey REFERENCES cca_usouconstipo DEFERRABLE INITIALLY DEFERRED,
    anio_construccion INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_anio_construccion_check CHECK( anio_construccion BETWEEN 1550 AND 2500),
    area_construida DOUBLE NOT NULL CONSTRAINT cca_crctrstcnddcnstrccion_area_construida_check CHECK( area_construida BETWEEN 0.0 AND 9.99999999999999E13),
    area_privada_construida DOUBLE NULL CONSTRAINT cca_crctrstcnddcnstrccion_area_privada_construida_check CHECK( area_privada_construida BETWEEN 0.0 AND 9.99999999999999E13),
    tipo_anexo INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_anexo_fkey REFERENCES cca_anexotipo DEFERRABLE INITIALLY DEFERRED,
    tipo_tipologia INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_tipologia_fkey REFERENCES cca_tipologiatipo DEFERRABLE INITIALLY DEFERRED,
    observaciones TEXT(250) NULL,
    calificacion_convencional INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_calificacion_convencional_fkey REFERENCES cca_calificacionconvencional DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_calificacionconvencional" : """CREATE TABLE cca_calificacionconvencional (
  	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo_calificar INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_tipo_calificar_fkey REFERENCES cca_calificartipo DEFERRABLE INITIALLY DEFERRED,
    total_calificacion INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_total_calificacion_check CHECK( total_calificacion BETWEEN 0 AND 999999999),
    clase_calificacion INTEGER NULL CONSTRAINT cca_calificacionconvencnal_clase_calificacion_fkey REFERENCES cca_clasecalificaciontipo DEFERRABLE INITIALLY DEFERRED,
    armazon INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_armazon_fkey REFERENCES cca_armazontipo DEFERRABLE INITIALLY DEFERRED,
    muros INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_muros_fkey REFERENCES cca_murostipo DEFERRABLE INITIALLY DEFERRED,
    cubierta INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_cubierta_fkey REFERENCES cca_cubiertatipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_estructura INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_conservacion_estructura_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_estructura INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_subtotal_estructura_check CHECK( subtotal_estructura BETWEEN 0 AND 9999999),
    fachada INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_fachada_fkey REFERENCES cca_fachadatipo DEFERRABLE INITIALLY DEFERRED,
    cubrimiento_muros INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_cubrimiento_muros_fkey REFERENCES cca_cubrimientomurostipo DEFERRABLE INITIALLY DEFERRED,
    piso INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_piso_fkey REFERENCES cca_pisotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_acabados INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_conservacion_acabados_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_acabados INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_subtotal_acabados_check CHECK( subtotal_acabados BETWEEN 0 AND 9999999),
    tamanio_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_tamanio_banio_fkey REFERENCES cca_tamaniobaniotipo DEFERRABLE INITIALLY DEFERRED,
    enchape_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_enchape_banio_fkey REFERENCES cca_enchapetipo DEFERRABLE INITIALLY DEFERRED,
    mobiliario_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_mobiliario_banio_fkey REFERENCES cca_mobiliariotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_conservacion_banio_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_banio INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_banio_check CHECK( subtotal_banio BETWEEN 0 AND 9999999),
    tamanio_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_tamanio_cocina_fkey REFERENCES cca_tamaniococinatipo DEFERRABLE INITIALLY DEFERRED,
    enchape_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_enchape_cocina_fkey REFERENCES cca_enchapetipo DEFERRABLE INITIALLY DEFERRED,
    mobiliario_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_mobiliario_cocina_fkey REFERENCES cca_mobiliariotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_conservacion_cocina_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_cocina INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_cocina_check CHECK( subtotal_cocina BETWEEN 0 AND 9999999),
    cerchas INTEGER NULL CONSTRAINT cca_calificacionconvencnal_cerchas_fkey REFERENCES cca_cerchastipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_cerchas INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_cerchas_check CHECK( subtotal_cerchas BETWEEN 0 AND 9999999)
	);""",

    "cca_adjunto": """CREATE TABLE "cca_adjunto" (
	"T_Id"	INTEGER,
	"T_Seq"	TEXT,
	"archivo"	TEXT,
	"observaciones"	TEXT,
	"procedencia"	TEXT,
	"tipo_archivo"	REAL,
	"relacion_soporte"	REAL,
	"dependencia_ucons"	REAL,
	"ruta_modificada"	TEXT,
	"cca_construccion_adjunto"	REAL,
	"cca_fuenteadminstrtiva_adjunto"	TEXT,
	"cca_interesado_adjunto"	TEXT,
	"cca_unidadconstruccion_adjunto"	REAL,
	"cca_predio_adjunto"	REAL,
	"cca_puntocontrol_adjunto"	TEXT,
	"cca_puntolevantamiento_adjunto"	TEXT,
	"cca_puntolindero_adjunto"	TEXT,
	"cca_puntoreferencia_adjunto"	TEXT
	);"""
}

modelo_ideal = {
    "cca_agrupacioninteresados" : """CREATE TABLE cca_agrupacioninteresados (
  	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_agrupacioninteresados_tipo_fkey REFERENCES cca_grupointeresadotipo DEFERRABLE INITIALLY DEFERRED,
    nombre TEXT(40) NULL
	);""",

    "cca_omisiones" : """CREATE TABLE cca_omisiones (
  	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    numero_predial TEXT(30) NOT NULL,
    numero_predial_anterior TEXT(20) NULL,
    codigo_orip TEXT(3) NULL,
    matricula_inmobiliaria TEXT(80) NULL,
    nupre TEXT(11) NULL,
    area_terreno DOUBLE NULL CONSTRAINT cca_omisiones_area_terreno_check CHECK( area_terreno BETWEEN 0.0 AND 1.0E8),
    area_construccion DOUBLE NULL CONSTRAINT cca_omisiones_area_construccion_check CHECK( area_construccion BETWEEN 0.0 AND 1.0E9),
    clase_suelo INTEGER NULL CONSTRAINT cca_omisiones_clase_suelo_fkey REFERENCES cca_clasesuelotipo DEFERRABLE INITIALLY DEFERRED,
    condicion_predio INTEGER NULL CONSTRAINT cca_omisiones_condicion_predio_fkey REFERENCES cca_condicionprediotipo DEFERRABLE INITIALLY DEFERRED,
    destinacion_economica INTEGER NULL CONSTRAINT cca_omisiones_destinacion_economica_fkey REFERENCES cca_destinacioneconomicatipo DEFERRABLE INITIALLY DEFERRED,
    observacion TEXT(255) NULL,
    identificado BOOLEAN NULL,
    propietario TEXT(250) NULL
	);""",

    "cca_fuenteadministrativa" : """CREATE TABLE cca_fuenteadministrativa (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_fuenteadministrativa_tipo_fkey REFERENCES cca_fuenteadministrativatipo DEFERRABLE INITIALLY DEFERRED,
    numero_fuente TEXT(150) NULL,
    fecha_documento_fuente DATE NULL,
    ente_emisor TEXT(255) NULL,
    observacion TEXT(250) NULL
	);""",

    "cca_interesado" : """CREATE TABLE cca_interesado (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_interesado_tipo_fkey REFERENCES cca_interesadotipo DEFERRABLE INITIALLY DEFERRED,
    tipo_documento INTEGER NOT NULL CONSTRAINT cca_interesado_tipo_documento_fkey REFERENCES cca_interesadodocumentotipo DEFERRABLE INITIALLY DEFERRED,
    documento_identidad TEXT(50) NULL,
    primer_nombre TEXT(100) NULL,
    segundo_nombre TEXT(100) NULL,
    primer_apellido TEXT(100) NULL,
    segundo_apellido TEXT(100) NULL,
    sexo INTEGER NULL CONSTRAINT cca_interesado_sexo_fkey REFERENCES cca_sexotipo DEFERRABLE INITIALLY DEFERRED,
    grupo_etnico INTEGER NULL CONSTRAINT cca_interesado_grupo_etnico_fkey REFERENCES cca_grupoetnicotipo DEFERRABLE INITIALLY DEFERRED,
    razon_social TEXT(255) NULL,
    departamento TEXT(100) NULL,
    municipio TEXT(100) NULL,
    direccion_residencia TEXT(255) NULL,
    telefono TEXT(20) NULL,
    correo_electronico TEXT(100) NULL,
    autoriza_notificacion_correo INTEGER NULL CONSTRAINT cca_interesado_autoriza_notificacin_crreo_fkey REFERENCES cca_booleanotipo DEFERRABLE INITIALLY DEFERRED,
    estado_civil INTEGER NULL CONSTRAINT cca_interesado_estado_civil_fkey REFERENCES cca_estadociviltipo DEFERRABLE INITIALLY DEFERRED,
    nombre TEXT(255) NULL
	);""",

    "cca_miembros" : """CREATE TABLE cca_miembros (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    interesado INTEGER NOT NULL CONSTRAINT cca_miembros_interesado_fkey REFERENCES cca_interesado DEFERRABLE INITIALLY DEFERRED,
    agrupacion INTEGER NOT NULL CONSTRAINT cca_miembros_agrupacion_fkey REFERENCES cca_agrupacioninteresados DEFERRABLE INITIALLY DEFERRED,
    participacion DOUBLE NULL CONSTRAINT cca_miembros_participacion_check CHECK( participacion BETWEEN 0.0 AND 1.0)
	);""",

    "cca_predio" : """CREATE TABLE cca_predio (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    id_operacion TEXT(30) NOT NULL,
    departamento_municipio TEXT(5) NOT NULL,
    clase_suelo_registro INTEGER NULL CONSTRAINT cca_predio_clase_suelo_registro_fkey REFERENCES cca_clasesuelotipo DEFERRABLE INITIALLY DEFERRED,
    categoria_suelo INTEGER NULL CONSTRAINT cca_predio_categoria_suelo_fkey REFERENCES cca_categoriasuelotipo DEFERRABLE INITIALLY DEFERRED,
    validacion_datos_localizacion BOOLEAN NULL,
    codigo_homologado TEXT(11) NULL,
    codigo_homologado_fmi BOOLEAN NULL,
    nupre TEXT(11) NULL,
    numero_predial TEXT(30) NOT NULL,
    numero_predial_anterior TEXT(20) NULL,
    validacion_datos_catastrales BOOLEAN NULL,
    tiene_fmi INTEGER NULL CONSTRAINT cca_predio_tiene_fmi_fkey REFERENCES cca_booleanotipo DEFERRABLE INITIALLY DEFERRED,
    codigo_orip TEXT(3) NULL,
    matricula_inmobiliaria TEXT(30) NULL,
    estado_folio INTEGER NULL CONSTRAINT cca_predio_estado_folio_fkey REFERENCES cca_estadofoliotipo DEFERRABLE INITIALLY DEFERRED,
    tiene_area_registral INTEGER NULL CONSTRAINT cca_predio_tiene_area_registral_fkey REFERENCES cca_booleanotipo DEFERRABLE INITIALLY DEFERRED,
    area_registral_m2 DOUBLE NULL CONSTRAINT cca_predio_area_registral_m2_check CHECK( area_registral_m2 BETWEEN 0.0 AND 1.0E22),
    validacion_datos_registrales BOOLEAN NULL,
    condicion_predio INTEGER NULL CONSTRAINT cca_predio_condicion_predio_fkey REFERENCES cca_condicionprediotipo DEFERRABLE INITIALLY DEFERRED,
    total_unidades_privadas INTEGER NULL CONSTRAINT cca_predio_total_unidades_privadas_check CHECK( total_unidades_privadas BETWEEN 0 AND 99999999),
    numero_torres INTEGER NULL CONSTRAINT cca_predio_numero_torres_check CHECK( numero_torres BETWEEN 0 AND 1000),
    area_total_terreno DOUBLE NULL CONSTRAINT cca_predio_area_total_terreno_check CHECK( area_total_terreno BETWEEN 0.0 AND 9.999999999999998E13),
    area_total_terreno_privada DOUBLE NULL CONSTRAINT cca_predio_area_total_terreno_prvada_check CHECK( area_total_terreno_privada BETWEEN 0.0 AND 9.999999999999998E13),
    area_total_terreno_comun DOUBLE NULL CONSTRAINT cca_predio_area_total_terreno_comun_check CHECK( area_total_terreno_comun BETWEEN 0.0 AND 9.999999999999998E13),
    area_total_construida DOUBLE NULL CONSTRAINT cca_predio_area_total_construida_check CHECK( area_total_construida BETWEEN 0.0 AND 9.999999999999998E13),
    area_total_construida_privada DOUBLE NULL CONSTRAINT cca_predio_area_total_constrd_prvada_check CHECK( area_total_construida_privada BETWEEN 0.0 AND 9.999999999999998E13),
    area_total_construida_comun DOUBLE NULL CONSTRAINT cca_predio_area_total_construid_cmun_check CHECK( area_total_construida_comun BETWEEN 0.0 AND 9.999999999999998E13),
    predio_matriz TEXT(30) NULL,
    coeficiente_copropiedad DOUBLE NULL CONSTRAINT cca_predio_coeficiente_copropiedad_check CHECK( coeficiente_copropiedad BETWEEN 0.0 AND 100.0),
    validacion_condicion_predio BOOLEAN NULL,
    destinacion_economica INTEGER NULL CONSTRAINT cca_predio_destinacion_economica_fkey REFERENCES cca_destinacioneconomicatipo DEFERRABLE INITIALLY DEFERRED,
    validacion_destinacion_economica BOOLEAN NULL,
    predio_tipo INTEGER NULL CONSTRAINT cca_predio_predio_tipo_fkey REFERENCES cca_prediotipo DEFERRABLE INITIALLY DEFERRED,
    validacion_tipo_predio BOOLEAN NULL,
    validacion_derechos BOOLEAN NULL,
    resultado_visita INTEGER NULL CONSTRAINT cca_predio_resultado_visita_fkey REFERENCES cca_resultadovisitatipo DEFERRABLE INITIALLY DEFERRED,
    otro_cual_resultado_visita TEXT(255) NULL,
    suscribe_acta_colindancia INTEGER NULL CONSTRAINT cca_predio_suscribe_acta_colindancia_fkey REFERENCES cca_booleanotipo DEFERRABLE INITIALLY DEFERRED,
    valor_referencia DOUBLE NULL CONSTRAINT cca_predio_valor_referencia_check CHECK( valor_referencia BETWEEN 0.0 AND 9.99999999999999E14),
    fecha_visita_predial DATE NULL,
    tipo_documento_quien_atendio INTEGER NULL CONSTRAINT cca_predio_tipo_documento_quien_tndio_fkey REFERENCES cca_interesadodocumentotipo DEFERRABLE INITIALLY DEFERRED,
    numero_documento_quien_atendio TEXT(50) NULL,
    nombres_apellidos_quien_atendio TEXT(250) NULL,
    celular TEXT(20) NULL,
    correo_electronico TEXT(100) NULL,
    observaciones TEXT(250) NULL,
    despojo_abandono BOOLEAN NULL,
    estrato INTEGER NULL CONSTRAINT cca_predio_estrato_fkey REFERENCES cca_estratotipo DEFERRABLE INITIALLY DEFERRED,
    otro_cual_estrato TEXT(255) NULL,
    usuario INTEGER NULL CONSTRAINT cca_predio_usuario_fkey REFERENCES cca_usuario DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_ofertasmercadoinmobiliario" : """CREATE TABLE cca_ofertasmercadoinmobiliario (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo_oferta INTEGER NOT NULL CONSTRAINT cca_ofertasmercadoinmblrio_tipo_oferta_fkey REFERENCES cca_ofertatipo DEFERRABLE INITIALLY DEFERRED,
    valor_pedido DOUBLE NOT NULL CONSTRAINT cca_ofertasmercadonmblrio_valor_pedido_check CHECK( valor_pedido BETWEEN 0.0 AND 9.99999999999999E14),
    valor_negociado DOUBLE NOT NULL CONSTRAINT cca_ofertasmercadonmblrio_valor_negociado_check CHECK( valor_negociado BETWEEN 0.0 AND 9.99999999999999E14),
    fecha_captura_oferta DATE NOT NULL,
    tiempo_oferta_mercado INTEGER NULL CONSTRAINT cca_ofertasmercadonmblrio_tiempo_oferta_mercado_check CHECK( tiempo_oferta_mercado BETWEEN 0 AND 1000),
    nombre_oferente TEXT(255) NOT NULL,
    numero_contacto_oferente TEXT(20) NOT NULL,
    predio INTEGER NULL CONSTRAINT cca_ofertasmercadoinmblrio_predio_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_predio_copropiedad" : """CREATE TABLE cca_predio_copropiedad (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    unidad_predial INTEGER NOT NULL CONSTRAINT cca_predio_copropiedad_unidad_predial_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED,
    matriz INTEGER NOT NULL CONSTRAINT cca_predio_copropiedad_matriz_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED,
    coeficiente DOUBLE NULL CONSTRAINT cca_predio_copropiedad_coeficiente_check CHECK( coeficiente BETWEEN 0.0 AND 1.0),
    CONSTRAINT cca_predio_copropiedad_unidad_predial_key UNIQUE (unidad_predial)
	);""",

    "cca_predio_informalidad" : """CREATE TABLE cca_predio_informalidad (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    cca_predio_formal INTEGER NOT NULL CONSTRAINT cca_predio_informalidad_cca_predio_formal_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED,
    cca_predio_informal INTEGER NOT NULL CONSTRAINT cca_predio_informalidad_cca_predio_informal_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_restriccion" : """CREATE TABLE cca_restriccion (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_restriccion_tipo_fkey REFERENCES cca_restricciontipo DEFERRABLE INITIALLY DEFERRED,
    descripcion TEXT(255) NULL,
    predio INTEGER NOT NULL CONSTRAINT cca_restriccion_predio_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_derecho" : """CREATE TABLE cca_derecho (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo INTEGER NOT NULL CONSTRAINT cca_derecho_tipo_fkey REFERENCES cca_derechotipo DEFERRABLE INITIALLY DEFERRED,
    cuota_participacion DOUBLE NULL CONSTRAINT cca_derecho_cuota_participacion_check CHECK( cuota_participacion BETWEEN 0.0 AND 100.0),
    fraccion_derecho DOUBLE NULL CONSTRAINT cca_derecho_fraccion_derecho_check CHECK( fraccion_derecho BETWEEN 0.0 AND 100.0),
    fecha_inicio_tenencia DATE NULL,
    origen_derecho INTEGER NULL CONSTRAINT cca_derecho_origen_derecho_fkey REFERENCES cca_origenderechotipo DEFERRABLE INITIALLY DEFERRED,
    observacion TEXT(250) NULL,
    agrupacion_interesados INTEGER NULL CONSTRAINT cca_derecho_agrupacion_interesados_fkey REFERENCES cca_agrupacioninteresados DEFERRABLE INITIALLY DEFERRED,
    interesado INTEGER NULL CONSTRAINT cca_derecho_interesado_fkey REFERENCES cca_interesado DEFERRABLE INITIALLY DEFERRED,
    predio INTEGER NOT NULL CONSTRAINT cca_derecho_predio_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_fuenteadministrativa_derecho" : """CREATE TABLE cca_fuenteadministrativa_derecho (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    derecho INTEGER NOT NULL CONSTRAINT cca_fuenteadminstrtv_drcho_derecho_fkey REFERENCES cca_derecho DEFERRABLE INITIALLY DEFERRED,
    fuente_administrativa INTEGER NOT NULL CONSTRAINT cca_fuenteadminstrtv_drcho_fuente_administrativa_fkey REFERENCES cca_fuenteadministrativa DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_estructuraamenazariesgovulnerabilidad" : """CREATE TABLE cca_estructuraamenazariesgovulnerabilidad (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Seq INTEGER NULL,
    tipo_amenaza_riesgo_vulnerabilidad INTEGER NOT NULL CONSTRAINT cca_estrctrmnzrsgvlnrbldad_tipo_amenaza_rsg_vlnrbldad_fkey REFERENCES cca_amenazariesgovulnerabilidadtipo DEFERRABLE INITIALLY DEFERRED,
    observacion TEXT(255) NULL,
    cca_predio_amenazariesgovulnerabilidad INTEGER NULL CONSTRAINT cca_estrctrmnzrsgvlnrbldad_cca_predio_mnzrsgvlnrbldad_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_estructuranovedadfmi" : """CREATE TABLE cca_estructuranovedadfmi (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Seq INTEGER NULL,
    codigo_orip TEXT(4) NOT NULL,
    numero_fmi TEXT(80) NOT NULL,
    tipo_novedadfmi INTEGER NULL CONSTRAINT cca_estructuranovedadfmi_tipo_novedadfmi_fkey REFERENCES cca_estructuranovedadfmi_tipo_novedadfmi DEFERRABLE INITIALLY DEFERRED,
    cca_predio_novedad_fmi INTEGER NULL CONSTRAINT cca_estructuranovedadfmi_cca_predio_novedad_fmi_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_estructuranovedadnumeropredial" : """CREATE TABLE cca_estructuranovedadnumeropredial (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Seq INTEGER NULL,
    numero_predial TEXT(30) NOT NULL,
    tipo_novedad INTEGER NOT NULL CONSTRAINT cca_estructurnvddnmrprdial_tipo_novedad_fkey REFERENCES cca_estructuranovedadnumeropredial_tipo_novedad DEFERRABLE INITIALLY DEFERRED,
    cca_predio_novedad_numeros_prediales INTEGER NULL CONSTRAINT cca_estructurnvddnmrprdial_cca_predi_nvdd_nmrs_prdles_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_usuario" : """CREATE TABLE cca_usuario (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    id TEXT(20) NULL,
    tipo_documento INTEGER NOT NULL CONSTRAINT cca_usuario_tipo_documento_fkey REFERENCES cca_interesadodocumentotipo DEFERRABLE INITIALLY DEFERRED,
    numero_documento TEXT(20) NOT NULL,
    coordinador TEXT(255) NULL,
    estado INTEGER NULL CONSTRAINT cca_usuario_estado_fkey REFERENCES cca_estadotipo DEFERRABLE INITIALLY DEFERRED,
    departamento_municipio_codigo TEXT(5) NULL,
    nombre TEXT(150) NOT NULL,
    contrasena TEXT(20) NULL,
    rol INTEGER NOT NULL CONSTRAINT cca_usuario_rol_fkey REFERENCES cca_roltipo DEFERRABLE INITIALLY DEFERRED,
    "municipio_codigo" TEXT(20)
	);""",

    "cca_caracteristicasunidadconstruccion" : """CREATE TABLE cca_caracteristicasunidadconstruccion (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    identificador TEXT(5) NOT NULL,
    tipo_dominio INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_dominio_fkey REFERENCES cca_dominioconstrucciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_construccion INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_construccion_fkey REFERENCES cca_construcciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_unidad_construccion INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_unidad_construccion_fkey REFERENCES cca_unidadconstrucciontipo DEFERRABLE INITIALLY DEFERRED,
    tipo_planta INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_planta_fkey REFERENCES cca_construccionplantatipo DEFERRABLE INITIALLY DEFERRED,
    total_habitaciones INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_habitaciones_check CHECK( total_habitaciones BETWEEN 0 AND 999999),
    total_banios INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_banios_check CHECK( total_banios BETWEEN 0 AND 999999),
    total_locales INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_locales_check CHECK( total_locales BETWEEN 0 AND 999999),
    total_plantas INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_total_plantas_check CHECK( total_plantas BETWEEN 0 AND 150),
    uso INTEGER NOT NULL CONSTRAINT cca_crctrstcsnddcnstrccion_uso_fkey REFERENCES cca_usouconstipo DEFERRABLE INITIALLY DEFERRED,
    anio_construccion INTEGER NULL CONSTRAINT cca_crctrstcnddcnstrccion_anio_construccion_check CHECK( anio_construccion BETWEEN 1550 AND 2500),
    area_construida DOUBLE NOT NULL CONSTRAINT cca_crctrstcnddcnstrccion_area_construida_check CHECK( area_construida BETWEEN 0.0 AND 9.99999999999999E13),
    area_privada_construida DOUBLE NULL CONSTRAINT cca_crctrstcnddcnstrccion_area_privada_construida_check CHECK( area_privada_construida BETWEEN 0.0 AND 9.99999999999999E13),
    tipo_anexo INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_anexo_fkey REFERENCES cca_anexotipo DEFERRABLE INITIALLY DEFERRED,
    tipo_tipologia INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_tipo_tipologia_fkey REFERENCES cca_tipologiatipo DEFERRABLE INITIALLY DEFERRED,
    observaciones TEXT(250) NULL,
    calificacion_convencional INTEGER NULL CONSTRAINT cca_crctrstcsnddcnstrccion_calificacion_convencional_fkey REFERENCES cca_calificacionconvencional DEFERRABLE INITIALLY DEFERRED
	);""",

    "cca_calificacionconvencional" : """CREATE TABLE cca_calificacionconvencional (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Ili_Tid TEXT(200) NULL,
    tipo_calificar INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_tipo_calificar_fkey REFERENCES cca_calificartipo DEFERRABLE INITIALLY DEFERRED,
    total_calificacion INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_total_calificacion_check CHECK( total_calificacion BETWEEN 0 AND 999999999),
    clase_calificacion INTEGER NULL CONSTRAINT cca_calificacionconvencnal_clase_calificacion_fkey REFERENCES cca_clasecalificaciontipo DEFERRABLE INITIALLY DEFERRED,
    armazon INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_armazon_fkey REFERENCES cca_armazontipo DEFERRABLE INITIALLY DEFERRED,
    muros INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_muros_fkey REFERENCES cca_murostipo DEFERRABLE INITIALLY DEFERRED,
    cubierta INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_cubierta_fkey REFERENCES cca_cubiertatipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_estructura INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_conservacion_estructura_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_estructura INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_subtotal_estructura_check CHECK( subtotal_estructura BETWEEN 0 AND 9999999),
    fachada INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_fachada_fkey REFERENCES cca_fachadatipo DEFERRABLE INITIALLY DEFERRED,
    cubrimiento_muros INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_cubrimiento_muros_fkey REFERENCES cca_cubrimientomurostipo DEFERRABLE INITIALLY DEFERRED,
    piso INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_piso_fkey REFERENCES cca_pisotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_acabados INTEGER NOT NULL CONSTRAINT cca_calificacionconvencnal_conservacion_acabados_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_acabados INTEGER NOT NULL CONSTRAINT cca_calificacionconvncnal_subtotal_acabados_check CHECK( subtotal_acabados BETWEEN 0 AND 9999999),
    tamanio_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_tamanio_banio_fkey REFERENCES cca_tamaniobaniotipo DEFERRABLE INITIALLY DEFERRED,
    enchape_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_enchape_banio_fkey REFERENCES cca_enchapetipo DEFERRABLE INITIALLY DEFERRED,
    mobiliario_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_mobiliario_banio_fkey REFERENCES cca_mobiliariotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_banio INTEGER NULL CONSTRAINT cca_calificacionconvencnal_conservacion_banio_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_banio INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_banio_check CHECK( subtotal_banio BETWEEN 0 AND 9999999),
    tamanio_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_tamanio_cocina_fkey REFERENCES cca_tamaniococinatipo DEFERRABLE INITIALLY DEFERRED,
    enchape_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_enchape_cocina_fkey REFERENCES cca_enchapetipo DEFERRABLE INITIALLY DEFERRED,
    mobiliario_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_mobiliario_cocina_fkey REFERENCES cca_mobiliariotipo DEFERRABLE INITIALLY DEFERRED,
    conservacion_cocina INTEGER NULL CONSTRAINT cca_calificacionconvencnal_conservacion_cocina_fkey REFERENCES cca_estadoconservaciontipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_cocina INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_cocina_check CHECK( subtotal_cocina BETWEEN 0 AND 9999999),
    cerchas INTEGER NULL CONSTRAINT cca_calificacionconvencnal_cerchas_fkey REFERENCES cca_cerchastipo DEFERRABLE INITIALLY DEFERRED,
    subtotal_cerchas INTEGER NULL CONSTRAINT cca_calificacionconvncnal_subtotal_cerchas_check CHECK( subtotal_cerchas BETWEEN 0 AND 9999999)
	);""",

    "cca_adjunto": """CREATE TABLE cca_adjunto (
	T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Seq INTEGER NULL,
    archivo TEXT(255) NULL,
    observaciones TEXT(255) NULL,
    procedencia TEXT(255) NULL,
    tipo_archivo INTEGER NULL CONSTRAINT cca_adjunto_tipo_archivo_fkey REFERENCES cca_adjunto_tipo_archivo DEFERRABLE INITIALLY DEFERRED,
    relacion_soporte INTEGER NULL CONSTRAINT cca_adjunto_relacion_soporte_fkey REFERENCES cca_adjunto_relacion_soporte DEFERRABLE INITIALLY DEFERRED,
    dependencia_ucons INTEGER NULL CONSTRAINT cca_adjunto_dependencia_ucons_fkey REFERENCES cca_adjunto_dependencia_ucons DEFERRABLE INITIALLY DEFERRED,
    ruta_modificada TEXT(150) NULL,
    cca_construccion_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_construccion_adjunto_fkey REFERENCES cca_construccion DEFERRABLE INITIALLY DEFERRED,
    cca_fuenteadminstrtiva_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_fuenteadminstrtv_djnto_fkey REFERENCES cca_fuenteadministrativa DEFERRABLE INITIALLY DEFERRED,
    cca_interesado_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_interesado_adjunto_fkey REFERENCES cca_interesado DEFERRABLE INITIALLY DEFERRED,
    cca_unidadconstruccion_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_unidadconstruccn_djnto_fkey REFERENCES cca_unidadconstruccion DEFERRABLE INITIALLY DEFERRED,
    cca_predio_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_predio_adjunto_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED,
    cca_puntocontrol_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_puntocontrol_adjunto_fkey REFERENCES cca_puntocontrol DEFERRABLE INITIALLY DEFERRED,
    cca_puntolevantamiento_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_puntolevantamint_djnto_fkey REFERENCES cca_puntolevantamiento DEFERRABLE INITIALLY DEFERRED,
    cca_puntolindero_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_puntolindero_adjunto_fkey REFERENCES cca_puntolindero DEFERRABLE INITIALLY DEFERRED,
    cca_puntoreferencia_adjunto INTEGER NULL CONSTRAINT cca_adjunto_cca_puntoreferencia_adjnto_fkey REFERENCES cca_puntoreferencia DEFERRABLE INITIALLY DEFERRED
	);"""


}

# Función para ejecutar una consulta SQL
def execute_query(conn, query):
    try:
        conn.execute(query)
        conn.commit()
        log_message(f"Consulta ejecutada con éxito: {query}")
    except sqlite3.Error as e:
        log_message(f"Error al ejecutar la consulta desde EXECUTE_QUERY: {e}")
        
def enable_foreign_keys(conn):
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        log_message("Claves foráneas habilitadas.")
    except sqlite3.Error as e:
        log_message(f"Error al habilitar claves foráneas: {e}")

def check_records(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    log_message(f"La tabla {table_name} contiene {count} registros antes de la migración.")
    return count

# Función para extraer tipos de datos de cada columna en la estructura de la tabla
def extract_column_types(create_table_sql):
    column_types = {}
    # Separar el SQL en líneas y omitir líneas que contienen "CONSTRAINT"
    lines = create_table_sql.strip().splitlines()

    log_message("Iniciando extracción de columnas y tipos de datos...")

    for line in lines:
        # Ignorar las líneas que contienen "CREATE TABLE" y otras que no sean columnas
        if "CREATE TABLE" in line.upper() or ");" in line:
            log_message(f"Saltando línea: {line.strip()}")
            continue

        # Registrar la línea que se está procesando
        log_message(f"Procesando línea: {line.strip()}")

        # Nueva expresión regular para manejar tipos con longitudes y restricciones opcionales
        match = re.match(r'\s*(\w+)\s+(\w+(?:\(\d+\))?)', line.strip())
        if match:
            column_name, data_type = match.groups()
            column_types[column_name] = data_type

            # Registrar lo que se ha extraído
            log_message(f"Columna extraída: {column_name}, Tipo de dato: {data_type}")
        else:
            log_message(f"No se encontró un match para la línea: {line.strip()}")

    log_message("Finalización de la extracción de columnas.\n")
    return column_types

# Función para crear la tabla con la estructura deseada
def create_new_table(conn, table_name, new_structure):
    try:
        execute_query(conn, f"DROP TABLE IF EXISTS {table_name}_old;")
        execute_query(conn, f"ALTER TABLE {table_name} RENAME TO {table_name}_old;")
        execute_query(conn, new_structure)
    except sqlite3.Error as e:
        log_message(f"Error al renombrar o crear la tabla {table_name}: {e}")



# Función para convertir y migrar los datos automáticamente
def convert_and_migrate_data(conn, table_name, column_types):
    cursor = conn.cursor()

    # Obtener las columnas y tipos de datos de la tabla antigua
    cursor.execute(f"PRAGMA table_info({table_name}_old);")
    old_columns_info = cursor.fetchall()

    # Imprimir las columnas antiguas y sus tipos de datos
    log_message(f"Estructura de la tabla {table_name}_old:")
    old_columns = []
    for col in old_columns_info:
        col_name = col[1]  # Nombre de la columna
        col_type = col[2]  # Tipo de dato de la columna
        old_columns.append(col_name)
        log_message(f"Columna: {col_name}, Tipo de dato: {col_type}")

    # Obtener las columnas y tipos de datos de la nueva tabla utilizando PRAGMA
    cursor.execute(f"PRAGMA table_info({table_name});")
    new_columns_info = cursor.fetchall()

    # Imprimir las columnas nuevas y sus tipos de datos
    log_message(f"Estructura de la nueva tabla (ideal):")
    new_c = []
    for col in new_columns_info:
        col_name = col[1]  # Nombre de la columna
        col_type = col[2]  # Tipo de dato de la columna
        new_c.append(col_name)
        log_message(f"Columna: {col_name}, Tipo de dato: {col_type}")

    # Obtener los datos de la tabla antigua
    cursor.execute(f"SELECT * FROM {table_name}_old;")
    rows = cursor.fetchall()
    if not rows:
        log_message(f"La tabla {table_name}_old está vacía o no se pudo leer correctamente.")
        return

    log_message(f"Tabla {table_name}_old leída con {len(rows)} registros.")
    
    # Mostrar los primeros 10 registros de la tabla antigua
    for i, row in enumerate(rows[:10]):
        log_message(f"Registro antiguo {i + 1}: {row}")
    
    # Obtener las columnas de la nueva tabla
    new_columns = list(column_types.keys())
    
    # Insertar cada registro en la nueva tabla con conversiones automáticas
    for row in rows:
        converted_row = []
        for idx, column in enumerate(new_columns):
            data_type = column_types[column]
            value = row[idx] if idx < len(row) else None
            # Verificación de valor None antes de convertir
            if value is None:
                converted_row.append(None)
            elif "INTEGER" in data_type:
                try:
                    converted_row.append(int(float(value)))
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a entero en columna {column}.")
                    converted_row.append(None)
            elif "REAL" in data_type:
                try:
                    converted_row.append(float(value) if value is not None else None)
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a FLOAT en columna {column}.")
                    converted_row.append(None)
            elif "DOUBLE" in data_type:
                try:
                    converted_row.append(float(value))  # Convertimos DOUBLE a float en Python
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a DOUBLE en columna {column}.")
                    converted_row.append(None)
            elif "DATE" in data_type:
                try:
                    converted_row.append(str(value))  # Mantiene el valor como cadena
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a DATE en columna {column}.")
                    converted_row.append(None)
            elif "BOOLEAN" in data_type:
                # Tratamos "1" o "true" como True, y "0" o "false" como False
                if isinstance(value, str):
                    if value.lower() in ("1", "true"):
                        converted_row.append(1)
                    elif value.lower() in ("0", "false"):
                        converted_row.append(0)
                    else:
                        log_message(f"Advertencia: valor '{value}' no es convertible a BOOLEAN en columna {column}.")
                        converted_row.append(None)
                elif isinstance(value, (int, float)):
                    converted_row.append(1 if value else 0)
                else:
                    converted_row.append(None)
            elif "TEXT" in data_type:
                converted_row.append(str(value) if value is not None else None)
            else:
                converted_row.append(None)  # Si el tipo de datos no coincide, se asigna None por defecto
        
        # Agregar log para depurar la conversión
        log_message(f"Registro convertido: {converted_row}")

        placeholders = ', '.join(['?' for _ in new_columns])
        query = f"INSERT INTO {table_name} ({', '.join(new_columns)}) VALUES ({placeholders})"
        
        # Imprimir la consulta y valores para depuración
        log_message(f"Query: {query}")
        log_message(f"Values: {converted_row}")

        try:
            cursor.execute(query, converted_row)
        except sqlite3.OperationalError as e:
            log_message(f"Error al ejecutar la consulta: {e}")
            log_message(f"Consulta: {query}")
            log_message(f"Valores: {converted_row}")
    
    conn.commit()
    
    # Confirmación de registros migrados a la nueva tabla
    cursor.execute(f"SELECT * FROM {table_name};")
    new_rows = cursor.fetchall()
    log_message(f"Tabla {table_name} tiene {len(new_rows)} registros después de la migración.")
    
    # Mostrar los primeros 10 registros migrados a la nueva tabla
    for i, row in enumerate(new_rows[:10]):
        log_message(f"Registro nuevo {i + 1}: {row}")

# Función para eliminar tablas '_old' después de la migración
def delete_old_tables(conn):
    cursor = conn.cursor()
    # Obtener el nombre de todas las tablas que terminan con '_old'
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_old';")
    old_tables = cursor.fetchall()
    
    if not old_tables:
        log_message("No se encontraron tablas '_old' para eliminar.")
        return
    
    for (old_table,) in old_tables:
        try:
            execute_query(conn, f"DROP TABLE IF EXISTS {old_table};")
            log_message(f"Tabla '{old_table}' eliminada con éxito.")
        except sqlite3.Error as e:
            log_message(f"Error al eliminar la tabla '{old_table}': {e}")

# Función principal para realizar la migración completa
def migrate_tables(conn, old_structure, new_structure):
    log_message("Inicio de la migración de tablas desde MIGRATE TABLES.")
    log_tables(conn)  # Verificar y listar tablas existentes antes de la migración
    
    for table_name, new_schema in new_structure.items():
        log_message(f"Migrando tabla {table_name}...")
        
        # Extraer tipos de datos de la estructura de la tabla nueva
        column_types = extract_column_types(new_schema)
        
        # Crear nueva tabla y renombrar la tabla antigua
        create_new_table(conn, table_name, new_schema)
        
        # Migrar datos con conversiones automáticas
        convert_and_migrate_data(conn, table_name, column_types)
        
        log_message(f"Tabla {table_name} migrada exitosamente.\n")

    # Llamar a la función para eliminar tablas '_old' al finalizar la migración
	#delete_old_tables(conn)

# Ejecutar el script de migración
def migrate_database():
    with sqlite3.connect(db_path) as conn:
        enable_foreign_keys(conn)
        
        # Iniciar el archivo de log en modo de escritura con UTF-8
        with codecs.open(log_path, "w", encoding="utf-8") as f:
            f.write("Inicio de la migración de tablas DESDE MIGRATE DATABASE\n")
        
        migrate_tables(conn, modelo_union, modelo_ideal)

    log_message("Migración completada.")
    print("Migración completada.")

# Llamar a la función principal de migración
if __name__ == "__main__":
    migrate_database()