
modelo_union = {

"""
CREATE TABLE "cca_agrupacioninteresados" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"nombre"	TEXT(40),
	CONSTRAINT "cca_agrupacioninteresados_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_grupointeresadotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);


CREATE TABLE "cca_omisiones" (
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
);

CREATE TABLE "cca_fuenteadministrativa" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"numero_fuente"	TEXT(150),
	"fecha_documento_fuente"	DATE,
	"ente_emisor"	TEXT(255),
	"observacion"	TEXT(250),
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_fuenteadministrativa_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_fuenteadministrativatipo" DEFERRABLE INITIALLY DEFERRED
);


CREATE TABLE "cca_interesado" (
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
);

CREATE TABLE "cca_miembros" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"interesado"	REAL,
	"agrupacion"	TEXT,
	"participacion"	TEXT
);

CREATE TABLE "cca_predio" (
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
);

CREATE TABLE "cca_ofertasmercadoinmobiliario" (
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
);

CREATE TABLE "cca_predio_copropiedad" (
	"T_Id"	TEXT,
	"unidad_predial"	TEXT,
	"matriz"	REAL,
	"coeficiente"	TEXT
);

CREATE TABLE "cca_predio_informalidad" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"cca_predio_formal"	TEXT,
	"cca_predio_informal"	REAL
);

CREATE TABLE "cca_restriccion" (
	"T_Id"	TEXT,
	"T_Ili_Tid"	TEXT,
	"tipo"	TEXT,
	"descripcion"	TEXT,
	"predio"	INTEGER
);

CREATE TABLE "cca_derecho" (
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
);

CREATE TABLE "cca_fuenteadministrativa_derecho" (
	"T_Id"	INTEGER,
	"T_Ili_Tid"	TEXT,
	"derecho"	REAL,
	"fuente_administrativa"	REAL
);

CREATE TABLE "cca_estructuraamenazariesgovulnerabilidad" (
	"T_Id"	TEXT,
	"T_Seq"	TEXT,
	"tipo_amenaza_riesgo_vulnerabilidad"	TEXT,
	"observacion"	TEXT,
	"cca_predio_amenazariesgovulnerabilidad"	INTEGER
);

CREATE TABLE "cca_estructuranovedadfmi" (
	"T_Id"	TEXT,
	"T_Seq"	TEXT,
	"codigo_orip"	TEXT,
	"numero_fmi"	TEXT,
	"tipo_novedadfmi"	TEXT,
	"cca_predio_novedad_fmi"	REAL
);

CREATE TABLE "cca_estructuranovedadnumeropredial" (
	"T_Id"	INTEGER,
	"T_Seq"	TEXT,
	"numero_predial"	TEXT,
	"tipo_novedad"	INTEGER,
	"cca_predio_novedad_numeros_prediales"	REAL
);

CREATE TABLE "cca_usuario" (
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
);

CREATE TABLE "cca_caracteristicasunidadconstruccion" (
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
);

CREATE TABLE "cca_calificacionconvencional" (
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
);

CREATE TABLE "cca_adjunto" (
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
);

#GEOMETRICAS
CREATE TABLE "cca_marcas" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"numero_predial"	TEXT,
	"codigo_orip"	TEXT,
	"matricula_inmobiliaria"	TEXT,
	"tipo"	INTEGER,
	"observacion"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);
"""
}
    