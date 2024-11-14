import re
import sqlite3
import os

# Ruta al archivo GeoPackage
db_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path = os.path.join(os.path.dirname(db_path), "migracion_log.txt")

# Función para escribir mensajes en el archivo de log
def log_message(message):
    with open(log_path, "a") as log_file:
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

    "cca_agrupacioninteresados" : """CREATE TABLE "cca_agrupacioninteresados" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"nombre"	TEXT(40),
	CONSTRAINT "cca_agrupacioninteresados_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_grupointeresadotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_omisiones" : """CREATE TABLE "cca_omisiones" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"numero_predial"	TEXT(30) NOT NULL,
	"numero_predial_anterior"	TEXT(20),
	"codigo_orip"	TEXT(3),
	"matricula_inmobiliaria"	TEXT(80),
	"nupre"	TEXT(11),
	"area_terreno"	DOUBLE CHECK("area_terreno" BETWEEN 0.0 AND 1.0E8),
	"area_construccion"	DOUBLE CHECK("area_construccion" BETWEEN 0.0 AND 1.0E9),
	"clase_suelo"	INTEGER,
	"condicion_predio"	INTEGER,
	"destinacion_economica"	INTEGER,
	"observacion"	TEXT(255),
	"identificado"	BOOLEAN,
	"propietario"	TEXT(250),
	CONSTRAINT "cca_omisiones_destinacion_economica_fkey" FOREIGN KEY("destinacion_economica") REFERENCES "cca_destinacioneconomicatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_omisiones_condicion_predio_fkey" FOREIGN KEY("condicion_predio") REFERENCES "cca_condicionprediotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_omisiones_clase_suelo_fkey" FOREIGN KEY("clase_suelo") REFERENCES "cca_clasesuelotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_fuenteadministrativa" : """CREATE TABLE "cca_fuenteadministrativa" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"numero_fuente"	TEXT(150),
	"fecha_documento_fuente"	DATE,
	"ente_emisor"	TEXT(255),
	"observacion"	TEXT(250),
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_fuenteadministrativa_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_fuenteadministrativatipo" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_interesado" : """CREATE TABLE "cca_interesado" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"tipo_documento"	INTEGER NOT NULL,
	"documento_identidad"	TEXT(50),
	"primer_nombre"	TEXT(100),
	"segundo_nombre"	TEXT(100),
	"primer_apellido"	TEXT(100),
	"segundo_apellido"	TEXT(100),
	"sexo"	INTEGER,
	"grupo_etnico"	INTEGER,
	"razon_social"	TEXT(255),
	"departamento"	TEXT(100),
	"municipio"	TEXT(100),
	"direccion_residencia"	TEXT(255),
	"telefono"	TEXT(20),
	"correo_electronico"	TEXT(100),
	"autoriza_notificacion_correo"	INTEGER,
	"estado_civil"	INTEGER,
	"nombre"	TEXT(255),
	CONSTRAINT "cca_interesado_tipo_documento_fkey" FOREIGN KEY("tipo_documento") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_estado_civil_fkey" FOREIGN KEY("estado_civil") REFERENCES "cca_estadociviltipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_grupo_etnico_fkey" FOREIGN KEY("grupo_etnico") REFERENCES "cca_grupoetnicotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_sexo_fkey" FOREIGN KEY("sexo") REFERENCES "cca_sexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_interesadotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_autoriza_notificacin_crreo_fkey" FOREIGN KEY("autoriza_notificacion_correo") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
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

    "cca_usuario" : """CREATE TABLE "cca_usuario" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"id"	TEXT(20),
	"tipo_documento"	INTEGER NOT NULL,
	"numero_documento"	TEXT(20) NOT NULL,
	"coordinador"	TEXT(255),
	"estado"	INTEGER,
	"departamento_municipio_codigo"	TEXT(5),
	"nombre"	TEXT(150) NOT NULL,
	"contrasena"	TEXT(20),
	"rol"	INTEGER NOT NULL,
	"municipio_codigo"	TEXT(20),
	CONSTRAINT "cca_usuario_tipo_documento_fkey" FOREIGN KEY("tipo_documento") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_usuario_estado_fkey" FOREIGN KEY("estado") REFERENCES "cca_estadotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_usuario_rol_fkey" FOREIGN KEY("rol") REFERENCES "cca_roltipo" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_caracteristicasunidadconstruccion" : """CREATE TABLE "cca_caracteristicasunidadconstruccion" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"identificador"	TEXT(5) NOT NULL,
	"tipo_dominio"	INTEGER,
	"tipo_construccion"	INTEGER,
	"tipo_unidad_construccion"	INTEGER NOT NULL,
	"tipo_planta"	INTEGER NOT NULL,
	"total_habitaciones"	INTEGER CHECK("total_habitaciones" BETWEEN 0 AND 999999),
	"total_banios"	INTEGER CHECK("total_banios" BETWEEN 0 AND 999999),
	"total_locales"	INTEGER CHECK("total_locales" BETWEEN 0 AND 999999),
	"total_plantas"	INTEGER CHECK("total_plantas" BETWEEN 0 AND 150),
	"uso"	INTEGER NOT NULL,
	"anio_construccion"	INTEGER CHECK("anio_construccion" BETWEEN 1550 AND 2500),
	"area_construida"	DOUBLE NOT NULL CHECK("area_construida" BETWEEN 0.0 AND 9.99999999999999E13),
	"area_privada_construida"	DOUBLE CHECK("area_privada_construida" BETWEEN 0.0 AND 9.99999999999999E13),
	"tipo_anexo"	INTEGER,
	"tipo_tipologia"	INTEGER,
	"observaciones"	TEXT(250),
	"calificacion_convencional"	INTEGER,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_dominio_fkey" FOREIGN KEY("tipo_dominio") REFERENCES "cca_dominioconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_construccion_fkey" FOREIGN KEY("tipo_construccion") REFERENCES "cca_construcciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_unidad_construccion_fkey" FOREIGN KEY("tipo_unidad_construccion") REFERENCES "cca_unidadconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_planta_fkey" FOREIGN KEY("tipo_planta") REFERENCES "cca_construccionplantatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_uso_fkey" FOREIGN KEY("uso") REFERENCES "cca_usouconstipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_calificacion_convencional_fkey" FOREIGN KEY("calificacion_convencional") REFERENCES "cca_calificacionconvencional" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_anexo_fkey" FOREIGN KEY("tipo_anexo") REFERENCES "cca_anexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_tipologia_fkey" FOREIGN KEY("tipo_tipologia") REFERENCES "cca_tipologiatipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_calificacionconvencional" : """CREATE TABLE "cca_calificacionconvencional" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo_calificar"	INTEGER NOT NULL,
	"total_calificacion"	INTEGER NOT NULL CHECK("total_calificacion" BETWEEN 0 AND 999999999),
	"clase_calificacion"	INTEGER,
	"armazon"	INTEGER NOT NULL,
	"muros"	INTEGER NOT NULL,
	"cubierta"	INTEGER NOT NULL,
	"conservacion_estructura"	INTEGER NOT NULL,
	"subtotal_estructura"	INTEGER NOT NULL CHECK("subtotal_estructura" BETWEEN 0 AND 9999999),
	"fachada"	INTEGER NOT NULL,
	"cubrimiento_muros"	INTEGER NOT NULL,
	"piso"	INTEGER NOT NULL,
	"conservacion_acabados"	INTEGER NOT NULL,
	"subtotal_acabados"	INTEGER NOT NULL CHECK("subtotal_acabados" BETWEEN 0 AND 9999999),
	"tamanio_banio"	INTEGER,
	"enchape_banio"	INTEGER,
	"mobiliario_banio"	INTEGER,
	"conservacion_banio"	INTEGER,
	"subtotal_banio"	INTEGER CHECK("subtotal_banio" BETWEEN 0 AND 9999999),
	"tamanio_cocina"	INTEGER,
	"enchape_cocina"	INTEGER,
	"mobiliario_cocina"	INTEGER,
	"conservacion_cocina"	INTEGER,
	"subtotal_cocina"	INTEGER CHECK("subtotal_cocina" BETWEEN 0 AND 9999999),
	"cerchas"	INTEGER,
	"subtotal_cerchas"	INTEGER CHECK("subtotal_cerchas" BETWEEN 0 AND 9999999),
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_calificacionconvencnal_armazon_fkey" FOREIGN KEY("armazon") REFERENCES "cca_armazontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tipo_calificar_fkey" FOREIGN KEY("tipo_calificar") REFERENCES "cca_calificartipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cubierta_fkey" FOREIGN KEY("cubierta") REFERENCES "cca_cubiertatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_clase_calificacion_fkey" FOREIGN KEY("clase_calificacion") REFERENCES "cca_clasecalificaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_muros_fkey" FOREIGN KEY("muros") REFERENCES "cca_murostipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_acabados_fkey" FOREIGN KEY("conservacion_acabados") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_piso_fkey" FOREIGN KEY("piso") REFERENCES "cca_pisotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tamanio_banio_fkey" FOREIGN KEY("tamanio_banio") REFERENCES "cca_tamaniobaniotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_banio_fkey" FOREIGN KEY("conservacion_banio") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cubrimiento_muros_fkey" FOREIGN KEY("cubrimiento_muros") REFERENCES "cca_cubrimientomurostipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tamanio_cocina_fkey" FOREIGN KEY("tamanio_cocina") REFERENCES "cca_tamaniococinatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_mobiliario_banio_fkey" FOREIGN KEY("mobiliario_banio") REFERENCES "cca_mobiliariotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_cocina_fkey" FOREIGN KEY("conservacion_cocina") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cerchas_fkey" FOREIGN KEY("cerchas") REFERENCES "cca_cerchastipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_estructura_fkey" FOREIGN KEY("conservacion_estructura") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_fachada_fkey" FOREIGN KEY("fachada") REFERENCES "cca_fachadatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_enchape_banio_fkey" FOREIGN KEY("enchape_banio") REFERENCES "cca_enchapetipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_mobiliario_cocina_fkey" FOREIGN KEY("mobiliario_cocina") REFERENCES "cca_mobiliariotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_enchape_cocina_fkey" FOREIGN KEY("enchape_cocina") REFERENCES "cca_enchapetipo" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_adjunto": """CREATE TABLE "cca_adjunto" (
        "T_Id" INTEGER,
        "T_Seq" TEXT,
        "archivo" TEXT,
        "observaciones" TEXT,
        "procedencia" TEXT,
        "tipo_archivo" REAL,
        "relacion_soporte" REAL,
        "dependencia_ucons" REAL,
        "ruta_modificada" TEXT,
        "cca_construccion_adjunto" REAL,
        "cca_fuenteadminstrtiva_adjunto" TEXT,
        "cca_interesado_adjunto" TEXT,
        "cca_unidadconstruccion_adjunto" REAL,
        "cca_predio_adjunto" REAL,
        "cca_puntocontrol_adjunto" TEXT,
        "cca_puntolevantamiento_adjunto" TEXT,
        "cca_puntolindero_adjunto" TEXT,
        "cca_puntoreferencia_adjunto" TEXT
    );"""
}

modelo_ideal = {
    "cca_agrupacioninteresados" : """CREATE TABLE "cca_agrupacioninteresados" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"nombre"	TEXT(40),
	CONSTRAINT "cca_agrupacioninteresados_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_grupointeresadotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_omisiones" : """CREATE TABLE "cca_omisiones" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"numero_predial"	TEXT(30) NOT NULL,
	"numero_predial_anterior"	TEXT(20),
	"codigo_orip"	TEXT(3),
	"matricula_inmobiliaria"	TEXT(80),
	"nupre"	TEXT(11),
	"area_terreno"	DOUBLE CHECK("area_terreno" BETWEEN 0.0 AND 1.0E8),
	"area_construccion"	DOUBLE CHECK("area_construccion" BETWEEN 0.0 AND 1.0E9),
	"clase_suelo"	INTEGER,
	"condicion_predio"	INTEGER,
	"destinacion_economica"	INTEGER,
	"observacion"	TEXT(255),
	"identificado"	BOOLEAN,
	"propietario"	TEXT(250),
	CONSTRAINT "cca_omisiones_destinacion_economica_fkey" FOREIGN KEY("destinacion_economica") REFERENCES "cca_destinacioneconomicatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_omisiones_condicion_predio_fkey" FOREIGN KEY("condicion_predio") REFERENCES "cca_condicionprediotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_omisiones_clase_suelo_fkey" FOREIGN KEY("clase_suelo") REFERENCES "cca_clasesuelotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_fuenteadministrativa" : """CREATE TABLE "cca_fuenteadministrativa" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"numero_fuente"	TEXT(150),
	"fecha_documento_fuente"	DATE,
	"ente_emisor"	TEXT(255),
	"observacion"	TEXT(250),
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_fuenteadministrativa_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_fuenteadministrativatipo" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_interesado" : """CREATE TABLE "cca_interesado" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"tipo_documento"	INTEGER NOT NULL,
	"documento_identidad"	TEXT(50),
	"primer_nombre"	TEXT(100),
	"segundo_nombre"	TEXT(100),
	"primer_apellido"	TEXT(100),
	"segundo_apellido"	TEXT(100),
	"sexo"	INTEGER,
	"grupo_etnico"	INTEGER,
	"razon_social"	TEXT(255),
	"departamento"	TEXT(100),
	"municipio"	TEXT(100),
	"direccion_residencia"	TEXT(255),
	"telefono"	TEXT(20),
	"correo_electronico"	TEXT(100),
	"autoriza_notificacion_correo"	INTEGER,
	"estado_civil"	INTEGER,
	"nombre"	TEXT(255),
	CONSTRAINT "cca_interesado_tipo_documento_fkey" FOREIGN KEY("tipo_documento") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_interesadotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_sexo_fkey" FOREIGN KEY("sexo") REFERENCES "cca_sexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_grupo_etnico_fkey" FOREIGN KEY("grupo_etnico") REFERENCES "cca_grupoetnicotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_estado_civil_fkey" FOREIGN KEY("estado_civil") REFERENCES "cca_estadociviltipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_autoriza_notificacin_crreo_fkey" FOREIGN KEY("autoriza_notificacion_correo") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_miembros" : """CREATE TABLE "cca_miembros" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"interesado"	INTEGER NOT NULL,
	"agrupacion"	INTEGER NOT NULL,
	"participacion"	DOUBLE CHECK("participacion" BETWEEN 0.0 AND 1.0),
	CONSTRAINT "cca_miembros_interesado_fkey" FOREIGN KEY("interesado") REFERENCES "cca_interesado" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_miembros_agrupacion_fkey" FOREIGN KEY("agrupacion") REFERENCES "cca_agrupacioninteresados" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_predio" : """CREATE TABLE "cca_predio" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"id_operacion"	TEXT(30) NOT NULL,
	"departamento_municipio"	TEXT(5) NOT NULL,
	"clase_suelo_registro"	INTEGER,
	"categoria_suelo"	INTEGER,
	"validacion_datos_localizacion"	BOOLEAN,
	"codigo_homologado"	TEXT(11),
	"codigo_homologado_fmi"	BOOLEAN,
	"nupre"	TEXT(11),
	"numero_predial"	TEXT(30) NOT NULL,
	"numero_predial_anterior"	TEXT(20),
	"validacion_datos_catastrales"	BOOLEAN,
	"tiene_fmi"	INTEGER,
	"codigo_orip"	TEXT(3),
	"matricula_inmobiliaria"	TEXT(30),
	"estado_folio"	INTEGER,
	"tiene_area_registral"	INTEGER,
	"area_registral_m2"	DOUBLE CHECK("area_registral_m2" BETWEEN 0.0 AND 1.0E22),
	"validacion_datos_registrales"	BOOLEAN,
	"condicion_predio"	INTEGER,
	"total_unidades_privadas"	INTEGER CHECK("total_unidades_privadas" BETWEEN 0 AND 99999999),
	"numero_torres"	INTEGER CHECK("numero_torres" BETWEEN 0 AND 1000),
	"area_total_terreno"	DOUBLE CHECK("area_total_terreno" BETWEEN 0.0 AND 9.999999999999998E13),
	"area_total_terreno_privada"	DOUBLE CHECK("area_total_terreno_privada" BETWEEN 0.0 AND 9.999999999999998E13),
	"area_total_terreno_comun"	DOUBLE CHECK("area_total_terreno_comun" BETWEEN 0.0 AND 9.999999999999998E13),
	"area_total_construida"	DOUBLE CHECK("area_total_construida" BETWEEN 0.0 AND 9.999999999999998E13),
	"area_total_construida_privada"	DOUBLE CHECK("area_total_construida_privada" BETWEEN 0.0 AND 9.999999999999998E13),
	"area_total_construida_comun"	DOUBLE CHECK("area_total_construida_comun" BETWEEN 0.0 AND 9.999999999999998E13),
	"predio_matriz"	TEXT(30),
	"coeficiente_copropiedad"	DOUBLE CHECK("coeficiente_copropiedad" BETWEEN 0.0 AND 100.0),
	"validacion_condicion_predio"	BOOLEAN,
	"destinacion_economica"	INTEGER,
	"validacion_destinacion_economica"	BOOLEAN,
	"predio_tipo"	INTEGER,
	"validacion_tipo_predio"	BOOLEAN,
	"validacion_derechos"	BOOLEAN,
	"resultado_visita"	INTEGER,
	"otro_cual_resultado_visita"	TEXT(255),
	"suscribe_acta_colindancia"	INTEGER,
	"valor_referencia"	DOUBLE CHECK("valor_referencia" BETWEEN 0.0 AND 9.99999999999999E14),
	"fecha_visita_predial"	DATE,
	"tipo_documento_quien_atendio"	INTEGER,
	"numero_documento_quien_atendio"	TEXT(50),
	"nombres_apellidos_quien_atendio"	TEXT(250),
	"celular"	TEXT(20),
	"correo_electronico"	TEXT(100),
	"observaciones"	TEXT(250),
	"despojo_abandono"	BOOLEAN,
	"estrato"	INTEGER,
	"otro_cual_estrato"	TEXT(255),
	"usuario"	INTEGER,
	CONSTRAINT "cca_predio_tipo_documento_quien_tndio_fkey" FOREIGN KEY("tipo_documento_quien_atendio") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_condicion_predio_fkey" FOREIGN KEY("condicion_predio") REFERENCES "cca_condicionprediotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_estrato_fkey" FOREIGN KEY("estrato") REFERENCES "cca_estratotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_predio_tipo_fkey" FOREIGN KEY("predio_tipo") REFERENCES "cca_prediotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_tiene_area_registral_fkey" FOREIGN KEY("tiene_area_registral") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_destinacion_economica_fkey" FOREIGN KEY("destinacion_economica") REFERENCES "cca_destinacioneconomicatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_usuario_fkey" FOREIGN KEY("usuario") REFERENCES "cca_usuario" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_clase_suelo_registro_fkey" FOREIGN KEY("clase_suelo_registro") REFERENCES "cca_clasesuelotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_suscribe_acta_colindancia_fkey" FOREIGN KEY("suscribe_acta_colindancia") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_tiene_fmi_fkey" FOREIGN KEY("tiene_fmi") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_categoria_suelo_fkey" FOREIGN KEY("categoria_suelo") REFERENCES "cca_categoriasuelotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_resultado_visita_fkey" FOREIGN KEY("resultado_visita") REFERENCES "cca_resultadovisitatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_estado_folio_fkey" FOREIGN KEY("estado_folio") REFERENCES "cca_estadofoliotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_ofertasmercadoinmobiliario" : """CREATE TABLE "cca_ofertasmercadoinmobiliario" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo_oferta"	INTEGER NOT NULL,
	"valor_pedido"	DOUBLE NOT NULL CHECK("valor_pedido" BETWEEN 0.0 AND 9.99999999999999E14),
	"valor_negociado"	DOUBLE NOT NULL CHECK("valor_negociado" BETWEEN 0.0 AND 9.99999999999999E14),
	"fecha_captura_oferta"	DATE NOT NULL,
	"tiempo_oferta_mercado"	INTEGER CHECK("tiempo_oferta_mercado" BETWEEN 0 AND 1000),
	"nombre_oferente"	TEXT(255) NOT NULL,
	"numero_contacto_oferente"	TEXT(20) NOT NULL,
	"predio"	INTEGER,
	CONSTRAINT "cca_ofertasmercadoinmblrio_tipo_oferta_fkey" FOREIGN KEY("tipo_oferta") REFERENCES "cca_ofertatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_ofertasmercadoinmblrio_predio_fkey" FOREIGN KEY("predio") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_predio_copropiedad" : """CREATE TABLE "cca_predio_copropiedad" (
	"T_Id"	INTEGER NOT NULL,
	"unidad_predial"	INTEGER NOT NULL,
	"matriz"	INTEGER NOT NULL,
	"coeficiente"	DOUBLE CHECK("coeficiente" BETWEEN 0.0 AND 1.0),
	CONSTRAINT "cca_predio_copropiedad_unidad_predial_key" UNIQUE("unidad_predial"),
	CONSTRAINT "cca_predio_copropiedad_matriz_fkey" FOREIGN KEY("matriz") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_copropiedad_unidad_predial_fkey" FOREIGN KEY("unidad_predial") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_predio_informalidad" : """CREATE TABLE "cca_predio_informalidad" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"cca_predio_formal"	INTEGER NOT NULL,
	"cca_predio_informal"	INTEGER NOT NULL,
	CONSTRAINT "cca_predio_informalidad_cca_predio_informal_fkey" FOREIGN KEY("cca_predio_informal") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_informalidad_cca_predio_formal_fkey" FOREIGN KEY("cca_predio_formal") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_restriccion" : """CREATE TABLE "cca_restriccion" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"descripcion"	TEXT(255),
	"predio"	INTEGER NOT NULL,
	CONSTRAINT "cca_restriccion_predio_fkey" FOREIGN KEY("predio") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_restriccion_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_restricciontipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_derecho" : """CREATE TABLE "cca_derecho" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"cuota_participacion"	DOUBLE CHECK("cuota_participacion" BETWEEN 0.0 AND 100.0),
	"fraccion_derecho"	DOUBLE CHECK("fraccion_derecho" BETWEEN 0.0 AND 100.0),
	"fecha_inicio_tenencia"	DATE,
	"origen_derecho"	INTEGER,
	"observacion"	TEXT(250),
	"agrupacion_interesados"	INTEGER,
	"interesado"	INTEGER,
	"predio"	INTEGER NOT NULL,
	CONSTRAINT "cca_derecho_agrupacion_interesados_fkey" FOREIGN KEY("agrupacion_interesados") REFERENCES "cca_agrupacioninteresados" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_derecho_origen_derecho_fkey" FOREIGN KEY("origen_derecho") REFERENCES "cca_origenderechotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_derecho_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_derechotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_derecho_interesado_fkey" FOREIGN KEY("interesado") REFERENCES "cca_interesado" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_derecho_predio_fkey" FOREIGN KEY("predio") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_fuenteadministrativa_derecho" : """CREATE TABLE "cca_fuenteadministrativa_derecho" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"derecho"	INTEGER NOT NULL,
	"fuente_administrativa"	INTEGER NOT NULL,
	CONSTRAINT "cca_fuenteadminstrtv_drcho_derecho_fkey" FOREIGN KEY("derecho") REFERENCES "cca_derecho" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_fuenteadminstrtv_drcho_fuente_administrativa_fkey" FOREIGN KEY("fuente_administrativa") REFERENCES "cca_fuenteadministrativa" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_estructuraamenazariesgovulnerabilidad" : """CREATE TABLE "cca_estructuraamenazariesgovulnerabilidad" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"tipo_amenaza_riesgo_vulnerabilidad"	INTEGER NOT NULL,
	"observacion"	TEXT(255),
	"cca_predio_amenazariesgovulnerabilidad"	INTEGER,
	CONSTRAINT "cca_estrctrmnzrsgvlnrbldad_tipo_amenaza_rsg_vlnrbldad_fkey" FOREIGN KEY("tipo_amenaza_riesgo_vulnerabilidad") REFERENCES "cca_amenazariesgovulnerabilidadtipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estrctrmnzrsgvlnrbldad_cca_predio_mnzrsgvlnrbldad_fkey" FOREIGN KEY("cca_predio_amenazariesgovulnerabilidad") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_estructuranovedadfmi" : """CREATE TABLE "cca_estructuranovedadfmi" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"codigo_orip"	TEXT(4) NOT NULL,
	"numero_fmi"	TEXT(80) NOT NULL,
	"tipo_novedadfmi"	INTEGER,
	"cca_predio_novedad_fmi"	INTEGER,
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_estructuranovedadfmi_cca_predio_novedad_fmi_fkey" FOREIGN KEY("cca_predio_novedad_fmi") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estructuranovedadfmi_tipo_novedadfmi_fkey" FOREIGN KEY("tipo_novedadfmi") REFERENCES "cca_estructuranovedadfmi_tipo_novedadfmi" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_estructuranovedadnumeropredial" : """CREATE TABLE "cca_estructuranovedadnumeropredial" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"numero_predial"	TEXT(30) NOT NULL,
	"tipo_novedad"	INTEGER NOT NULL,
	"cca_predio_novedad_numeros_prediales"	INTEGER,
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_estructurnvddnmrprdial_tipo_novedad_fkey" FOREIGN KEY("tipo_novedad") REFERENCES "cca_estructuranovedadnumeropredial_tipo_novedad" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estructurnvddnmrprdial_cca_predi_nvdd_nmrs_prdles_fkey" FOREIGN KEY("cca_predio_novedad_numeros_prediales") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED
    );""",

    "cca_usuario" : """CREATE TABLE "cca_usuario" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"id"	TEXT(20),
	"tipo_documento"	INTEGER NOT NULL,
	"numero_documento"	TEXT(20) NOT NULL,
	"coordinador"	TEXT(255),
	"estado"	INTEGER,
	"departamento_municipio_codigo"	TEXT(5),
	"nombre"	TEXT(150) NOT NULL,
	"contrasena"	TEXT(20),
	"rol"	INTEGER NOT NULL,
	"municipio_codigo"	TEXT(20),
	CONSTRAINT "cca_usuario_estado_fkey" FOREIGN KEY("estado") REFERENCES "cca_estadotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_usuario_rol_fkey" FOREIGN KEY("rol") REFERENCES "cca_roltipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_usuario_tipo_documento_fkey" FOREIGN KEY("tipo_documento") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_caracteristicasunidadconstruccion" : """CREATE TABLE "cca_caracteristicasunidadconstruccion" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"identificador"	TEXT(5) NOT NULL,
	"tipo_dominio"	INTEGER,
	"tipo_construccion"	INTEGER,
	"tipo_unidad_construccion"	INTEGER NOT NULL,
	"tipo_planta"	INTEGER NOT NULL,
	"total_habitaciones"	INTEGER CHECK("total_habitaciones" BETWEEN 0 AND 999999),
	"total_banios"	INTEGER CHECK("total_banios" BETWEEN 0 AND 999999),
	"total_locales"	INTEGER CHECK("total_locales" BETWEEN 0 AND 999999),
	"total_plantas"	INTEGER CHECK("total_plantas" BETWEEN 0 AND 150),
	"uso"	INTEGER NOT NULL,
	"anio_construccion"	INTEGER CHECK("anio_construccion" BETWEEN 1550 AND 2500),
	"area_construida"	DOUBLE NOT NULL CHECK("area_construida" BETWEEN 0.0 AND 9.99999999999999E13),
	"area_privada_construida"	DOUBLE CHECK("area_privada_construida" BETWEEN 0.0 AND 9.99999999999999E13),
	"tipo_anexo"	INTEGER,
	"tipo_tipologia"	INTEGER,
	"observaciones"	TEXT(250),
	"calificacion_convencional"	INTEGER,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_construccion_fkey" FOREIGN KEY("tipo_construccion") REFERENCES "cca_construcciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_unidad_construccion_fkey" FOREIGN KEY("tipo_unidad_construccion") REFERENCES "cca_unidadconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_dominio_fkey" FOREIGN KEY("tipo_dominio") REFERENCES "cca_dominioconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_uso_fkey" FOREIGN KEY("uso") REFERENCES "cca_usouconstipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_calificacion_convencional_fkey" FOREIGN KEY("calificacion_convencional") REFERENCES "cca_calificacionconvencional" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_anexo_fkey" FOREIGN KEY("tipo_anexo") REFERENCES "cca_anexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_tipologia_fkey" FOREIGN KEY("tipo_tipologia") REFERENCES "cca_tipologiatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_planta_fkey" FOREIGN KEY("tipo_planta") REFERENCES "cca_construccionplantatipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_calificacionconvencional" : """CREATE TABLE "cca_calificacionconvencional" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo_calificar"	INTEGER NOT NULL,
	"total_calificacion"	INTEGER NOT NULL CHECK("total_calificacion" BETWEEN 0 AND 999999999),
	"clase_calificacion"	INTEGER,
	"armazon"	INTEGER NOT NULL,
	"muros"	INTEGER NOT NULL,
	"cubierta"	INTEGER NOT NULL,
	"conservacion_estructura"	INTEGER NOT NULL,
	"subtotal_estructura"	INTEGER NOT NULL CHECK("subtotal_estructura" BETWEEN 0 AND 9999999),
	"fachada"	INTEGER NOT NULL,
	"cubrimiento_muros"	INTEGER NOT NULL,
	"piso"	INTEGER NOT NULL,
	"conservacion_acabados"	INTEGER NOT NULL,
	"subtotal_acabados"	INTEGER NOT NULL CHECK("subtotal_acabados" BETWEEN 0 AND 9999999),
	"tamanio_banio"	INTEGER,
	"enchape_banio"	INTEGER,
	"mobiliario_banio"	INTEGER,
	"conservacion_banio"	INTEGER,
	"subtotal_banio"	INTEGER CHECK("subtotal_banio" BETWEEN 0 AND 9999999),
	"tamanio_cocina"	INTEGER,
	"enchape_cocina"	INTEGER,
	"mobiliario_cocina"	INTEGER,
	"conservacion_cocina"	INTEGER,
	"subtotal_cocina"	INTEGER CHECK("subtotal_cocina" BETWEEN 0 AND 9999999),
	"cerchas"	INTEGER,
	"subtotal_cerchas"	INTEGER CHECK("subtotal_cerchas" BETWEEN 0 AND 9999999),
	CONSTRAINT "cca_calificacionconvencnal_enchape_banio_fkey" FOREIGN KEY("enchape_banio") REFERENCES "cca_enchapetipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_mobiliario_cocina_fkey" FOREIGN KEY("mobiliario_cocina") REFERENCES "cca_mobiliariotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_cocina_fkey" FOREIGN KEY("conservacion_cocina") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cerchas_fkey" FOREIGN KEY("cerchas") REFERENCES "cca_cerchastipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_mobiliario_banio_fkey" FOREIGN KEY("mobiliario_banio") REFERENCES "cca_mobiliariotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_banio_fkey" FOREIGN KEY("conservacion_banio") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tamanio_cocina_fkey" FOREIGN KEY("tamanio_cocina") REFERENCES "cca_tamaniococinatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_enchape_cocina_fkey" FOREIGN KEY("enchape_cocina") REFERENCES "cca_enchapetipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_piso_fkey" FOREIGN KEY("piso") REFERENCES "cca_pisotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_clase_calificacion_fkey" FOREIGN KEY("clase_calificacion") REFERENCES "cca_clasecalificaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_armazon_fkey" FOREIGN KEY("armazon") REFERENCES "cca_armazontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_fachada_fkey" FOREIGN KEY("fachada") REFERENCES "cca_fachadatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_estructura_fkey" FOREIGN KEY("conservacion_estructura") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cubierta_fkey" FOREIGN KEY("cubierta") REFERENCES "cca_cubiertatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tipo_calificar_fkey" FOREIGN KEY("tipo_calificar") REFERENCES "cca_calificartipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_cubrimiento_muros_fkey" FOREIGN KEY("cubrimiento_muros") REFERENCES "cca_cubrimientomurostipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_conservacion_acabados_fkey" FOREIGN KEY("conservacion_acabados") REFERENCES "cca_estadoconservaciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_muros_fkey" FOREIGN KEY("muros") REFERENCES "cca_murostipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_calificacionconvencnal_tamanio_banio_fkey" FOREIGN KEY("tamanio_banio") REFERENCES "cca_tamaniobaniotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );""",

    "cca_adjunto": """CREATE TABLE "cca_adjunto" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"archivo"	TEXT(255),
	"observaciones"	TEXT(255),
	"procedencia"	TEXT(255),
	"tipo_archivo"	INTEGER,
	"relacion_soporte"	INTEGER,
	"dependencia_ucons"	INTEGER,
	"ruta_modificada"	TEXT(150),
	"cca_construccion_adjunto"	INTEGER,
	"cca_fuenteadminstrtiva_adjunto"	INTEGER,
	"cca_interesado_adjunto"	INTEGER,
	"cca_unidadconstruccion_adjunto"	INTEGER,
	"cca_predio_adjunto"	INTEGER,
	"cca_puntocontrol_adjunto"	INTEGER,
	"cca_puntolevantamiento_adjunto"	INTEGER,
	"cca_puntolindero_adjunto"	INTEGER,
	"cca_puntoreferencia_adjunto"	INTEGER,
	CONSTRAINT "cca_adjunto_cca_puntolindero_adjunto_fkey" FOREIGN KEY("cca_puntolindero_adjunto") REFERENCES "cca_puntolindero" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_tipo_archivo_fkey" FOREIGN KEY("tipo_archivo") REFERENCES "cca_adjunto_tipo_archivo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_puntoreferencia_adjnto_fkey" FOREIGN KEY("cca_puntoreferencia_adjunto") REFERENCES "cca_puntoreferencia" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_relacion_soporte_fkey" FOREIGN KEY("relacion_soporte") REFERENCES "cca_adjunto_relacion_soporte" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_dependencia_ucons_fkey" FOREIGN KEY("dependencia_ucons") REFERENCES "cca_adjunto_dependencia_ucons" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_interesado_adjunto_fkey" FOREIGN KEY("cca_interesado_adjunto") REFERENCES "cca_interesado" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_fuenteadminstrtv_djnto_fkey" FOREIGN KEY("cca_fuenteadminstrtiva_adjunto") REFERENCES "cca_fuenteadministrativa" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_construccion_adjunto_fkey" FOREIGN KEY("cca_construccion_adjunto") REFERENCES "cca_construccion" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_unidadconstruccn_djnto_fkey" FOREIGN KEY("cca_unidadconstruccion_adjunto") REFERENCES "cca_unidadconstruccion" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_puntolevantamint_djnto_fkey" FOREIGN KEY("cca_puntolevantamiento_adjunto") REFERENCES "cca_puntolevantamiento" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_predio_adjunto_fkey" FOREIGN KEY("cca_predio_adjunto") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_adjunto_cca_puntocontrol_adjunto_fkey" FOREIGN KEY("cca_puntocontrol_adjunto") REFERENCES "cca_puntocontrol" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
    );"""


}

# Función para ejecutar una consulta SQL
def execute_query(conn, query):
    try:
        conn.execute(query)
        conn.commit()
        log_message(f"Consulta ejecutada con éxito: {query}")
    except sqlite3.Error as e:
        log_message(f"Error al ejecutar la consulta: {e}")

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
    for line in lines:
        if "CONSTRAINT" not in line:
            # Buscar coincidencias de nombre de columna y tipo de datos        
            match = re.match(r'\s*"(\w+)"\s+(\w+)', line.strip())
            if match:
                column_name, data_type = match.groups()
                column_types[column_name] = data_type
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
            value = row[idx]
            # Verificación de valor None antes de convertir
            if value is None:
                converted_row.append(None)
            elif data_type == "INTEGER":
                try:
                    converted_row.append(int(float(value)))
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a entero en columna {column}.")
                    converted_row.append(None)
            elif data_type == "REAL":
                converted_row.append(float(value) if value is not None else None)
            elif data_type == "DOUBLE":
                try:
                    converted_row.append(float(value))  # Convertimos DOUBLE a float en Python
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a DOUBLE en columna {column}.")
                    converted_row.append(None)
            elif data_type == "DATE":
                try:
                    # Asumimos que la fecha se almacena como TEXT en el formato 'YYYY-MM-DD' o similar
                    converted_row.append(str(value))  # Mantiene el valor como cadena
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a DATE en columna {column}.")
                    converted_row.append(None)
            elif data_type == "BOOLEAN":
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
            elif data_type == "TEXT":
                converted_row.append(str(value) if value is not None else None)
            else:
                converted_row.append(None)  # Si el tipo de datos no coincide, se asigna None por defecto
        
        placeholders = ', '.join(['?' for _ in new_columns])
        query = f"INSERT INTO {table_name} ({', '.join(new_columns)}) VALUES ({placeholders})"
        cursor.execute(query, converted_row)
    
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
    delete_old_tables(conn)

# Ejecutar el script de migración
with sqlite3.connect(db_path) as conn:
    # Iniciar el archivo de log
    with open(log_path, "w") as f:
        f.write("Inicio de la migración de tablas\n")

    migrate_tables(conn, modelo_union, modelo_ideal)

log_message("Migración completada.")
print("Migración completada.")

