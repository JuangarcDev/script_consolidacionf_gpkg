"""
# TABLAS ALFANUMERICAS
#ESTA NO
#ESTA NO, ESTA IGUAL EN AMBAS FUENTES DE DATOS.
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
	CONSTRAINT "cca_fuenteadministrativa_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_fuenteadministrativatipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);





#ESTA TAMPOCO
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
	CONSTRAINT "cca_interesado_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_interesadotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_sexo_fkey" FOREIGN KEY("sexo") REFERENCES "cca_sexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_grupo_etnico_fkey" FOREIGN KEY("grupo_etnico") REFERENCES "cca_grupoetnicotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_estado_civil_fkey" FOREIGN KEY("estado_civil") REFERENCES "cca_estadociviltipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_interesado_autoriza_notificacin_crreo_fkey" FOREIGN KEY("autoriza_notificacion_correo") REFERENCES "cca_booleanotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_miembros" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"interesado"	INTEGER NOT NULL,
	"agrupacion"	INTEGER NOT NULL,
	"participacion"	DOUBLE CHECK("participacion" BETWEEN 0.0 AND 1.0),
	CONSTRAINT "cca_miembros_interesado_fkey" FOREIGN KEY("interesado") REFERENCES "cca_interesado" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_miembros_agrupacion_fkey" FOREIGN KEY("agrupacion") REFERENCES "cca_agrupacioninteresados" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_predio" (
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
);

CREATE TABLE "cca_ofertasmercadoinmobiliario" (
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
);

CREATE TABLE "cca_predio_copropiedad" (
	"T_Id"	INTEGER NOT NULL,
	"unidad_predial"	INTEGER NOT NULL,
	"matriz"	INTEGER NOT NULL,
	"coeficiente"	DOUBLE CHECK("coeficiente" BETWEEN 0.0 AND 1.0),
	CONSTRAINT "cca_predio_copropiedad_unidad_predial_key" UNIQUE("unidad_predial"),
	CONSTRAINT "cca_predio_copropiedad_matriz_fkey" FOREIGN KEY("matriz") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_copropiedad_unidad_predial_fkey" FOREIGN KEY("unidad_predial") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_predio_informalidad" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"cca_predio_formal"	INTEGER NOT NULL,
	"cca_predio_informal"	INTEGER NOT NULL,
	CONSTRAINT "cca_predio_informalidad_cca_predio_informal_fkey" FOREIGN KEY("cca_predio_informal") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_predio_informalidad_cca_predio_formal_fkey" FOREIGN KEY("cca_predio_formal") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_restriccion" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"tipo"	INTEGER NOT NULL,
	"descripcion"	TEXT(255),
	"predio"	INTEGER NOT NULL,
	CONSTRAINT "cca_restriccion_predio_fkey" FOREIGN KEY("predio") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_restriccion_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_restricciontipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_derecho" (
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
);

CREATE TABLE "cca_fuenteadministrativa_derecho" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"derecho"	INTEGER NOT NULL,
	"fuente_administrativa"	INTEGER NOT NULL,
	CONSTRAINT "cca_fuenteadminstrtv_drcho_derecho_fkey" FOREIGN KEY("derecho") REFERENCES "cca_derecho" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_fuenteadminstrtv_drcho_fuente_administrativa_fkey" FOREIGN KEY("fuente_administrativa") REFERENCES "cca_fuenteadministrativa" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_estructuraamenazariesgovulnerabilidad" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"tipo_amenaza_riesgo_vulnerabilidad"	INTEGER NOT NULL,
	"observacion"	TEXT(255),
	"cca_predio_amenazariesgovulnerabilidad"	INTEGER,
	CONSTRAINT "cca_estrctrmnzrsgvlnrbldad_tipo_amenaza_rsg_vlnrbldad_fkey" FOREIGN KEY("tipo_amenaza_riesgo_vulnerabilidad") REFERENCES "cca_amenazariesgovulnerabilidadtipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estrctrmnzrsgvlnrbldad_cca_predio_mnzrsgvlnrbldad_fkey" FOREIGN KEY("cca_predio_amenazariesgovulnerabilidad") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_estructuranovedadfmi" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"codigo_orip"	TEXT(4) NOT NULL,
	"numero_fmi"	TEXT(80) NOT NULL,
	"tipo_novedadfmi"	INTEGER,
	"cca_predio_novedad_fmi"	INTEGER,
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_estructuranovedadfmi_cca_predio_novedad_fmi_fkey" FOREIGN KEY("cca_predio_novedad_fmi") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estructuranovedadfmi_tipo_novedadfmi_fkey" FOREIGN KEY("tipo_novedadfmi") REFERENCES "cca_estructuranovedadfmi_tipo_novedadfmi" DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "cca_estructuranovedadnumeropredial" (
	"T_Id"	INTEGER NOT NULL,
	"T_Seq"	INTEGER,
	"numero_predial"	TEXT(30) NOT NULL,
	"tipo_novedad"	INTEGER NOT NULL,
	"cca_predio_novedad_numeros_prediales"	INTEGER,
	PRIMARY KEY("T_Id"),
	CONSTRAINT "cca_estructurnvddnmrprdial_tipo_novedad_fkey" FOREIGN KEY("tipo_novedad") REFERENCES "cca_estructuranovedadnumeropredial_tipo_novedad" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_estructurnvddnmrprdial_cca_predi_nvdd_nmrs_prdles_fkey" FOREIGN KEY("cca_predio_novedad_numeros_prediales") REFERENCES "cca_predio" DEFERRABLE INITIALLY DEFERRED
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
	CONSTRAINT "cca_usuario_estado_fkey" FOREIGN KEY("estado") REFERENCES "cca_estadotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_usuario_rol_fkey" FOREIGN KEY("rol") REFERENCES "cca_roltipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_usuario_tipo_documento_fkey" FOREIGN KEY("tipo_documento") REFERENCES "cca_interesadodocumentotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
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
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_construccion_fkey" FOREIGN KEY("tipo_construccion") REFERENCES "cca_construcciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_unidad_construccion_fkey" FOREIGN KEY("tipo_unidad_construccion") REFERENCES "cca_unidadconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_dominio_fkey" FOREIGN KEY("tipo_dominio") REFERENCES "cca_dominioconstrucciontipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_uso_fkey" FOREIGN KEY("uso") REFERENCES "cca_usouconstipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_calificacion_convencional_fkey" FOREIGN KEY("calificacion_convencional") REFERENCES "cca_calificacionconvencional" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_anexo_fkey" FOREIGN KEY("tipo_anexo") REFERENCES "cca_anexotipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_tipologia_fkey" FOREIGN KEY("tipo_tipologia") REFERENCES "cca_tipologiatipo" DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT "cca_crctrstcsnddcnstrccion_tipo_planta_fkey" FOREIGN KEY("tipo_planta") REFERENCES "cca_construccionplantatipo" DEFERRABLE INITIALLY DEFERRED,
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
);

CREATE TABLE "cca_adjunto" (
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
);


# CAPAS GEOGRAFICAS

CREATE TABLE "cca_saldosconservacion" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"numero_predial"	TEXT(30) NOT NULL,
	"codigo_orip"	TEXT(3),
	"matricula_inmobiliaria"	TEXT(20),
	"tipo"	INTEGER,
	"observacion"	TEXT(255),
	"localizacion"	POINT,
	CONSTRAINT "cca_saldosconservacion_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_saldotipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_marcas" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"numero_predial"	TEXT(30) NOT NULL,
	"codigo_orip"	TEXT(3),
	"matricula_inmobiliaria"	TEXT(20),
	"tipo"	INTEGER,
	"observacion"	TEXT(250),
	"localizacion"	POINT,
	CONSTRAINT "cca_marcas_tipo_fkey" FOREIGN KEY("tipo") REFERENCES "cca_marcatipo" DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("T_Id")
);

CREATE TABLE "cca_unidadconstruccion" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"tipo_planta"	INTEGER,
	"planta_ubicacion"	INTEGER,
	"area_construida"	REAL,
	"altura"	REAL,
	"observaciones"	TEXT,
	"caracteristicasunidadconstruccion"	INTEGER,
	"construccion"	INTEGER,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_construccion" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"identificador"	TEXT,
	"tipo_construccion"	INTEGER,
	"tipo_dominio"	INTEGER,
	"numero_pisos"	INTEGER,
	"numero_sotanos"	INTEGER,
	"numero_mezanines"	INTEGER,
	"numero_semisotanos"	INTEGER,
	"area_construccion_alfanumerica"	REAL,
	"area_construccion_digital"	REAL,
	"anio_construccion"	INTEGER,
	"valor_referencia_construccion"	REAL,
	"etiqueta"	TEXT,
	"altura"	REAL,
	"observaciones"	TEXT,
	"predio"	INTEGER,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_puntocontrol" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"id_punto_control"	TEXT,
	"puntotipo"	INTEGER,
	"tipo_punto_control"	TEXT,
	"exactitud_horizontal"	REAL,
	"exactitud_vertical"	REAL,
	"posicion_interpolacion"	INTEGER,
	"metodo_produccion"	INTEGER,
	"observacion"	TEXT,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_puntolevantamiento" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"id_punto_levantamiento"	TEXT,
	"puntotipo"	INTEGER,
	"tipo_punto_levantamiento"	INTEGER,
	"fotoidentificacion"	INTEGER,
	"exactitud_horizontal"	REAL,
	"exactitud_vertical"	REAL,
	"posicion_interpolacion"	INTEGER,
	"metodo_produccion"	INTEGER,
	"observacion"	TEXT,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_puntolindero" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"id_punto_lindero"	TEXT,
	"puntotipo"	INTEGER,
	"acuerdo"	INTEGER,
	"fotoidentificacion"	INTEGER,
	"exactitud_horizontal"	REAL,
	"exactitud_vertical"	REAL,
	"posicion_interpolacion"	INTEGER,
	"metodo_produccion"	INTEGER,
	"observacion"	TEXT,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_puntoreferencia" (
	"fid"	INTEGER NOT NULL,
	"geom"	GEOMETRY,
	"T_Ili_Tid"	TEXT,
	"tipo_punto_referencia"	INTEGER,
	"cual"	TEXT,
	"posicion_interpolacion"	INTEGER,
	"metodo_produccion"	INTEGER,
	"observacion"	TEXT,
	"T_Id_Cop"	INTEGER,
	"Ruta"	TEXT,
	PRIMARY KEY("fid" AUTOINCREMENT)
);

CREATE TABLE "cca_comisiones" (
	"T_Id"	INTEGER NOT NULL,
	"T_Ili_Tid"	TEXT(200),
	"numero_predial"	TEXT(30) NOT NULL,
	"numero_predial_anterior"	TEXT(20),
	"area"	DOUBLE CHECK("area" BETWEEN 0.0 AND 1.0E8),
	"geometria"	MULTIPOLYGON,
	"observaciones"	TEXT(255),
	"identificado"	BOOLEAN,
	PRIMARY KEY("T_Id")
);
"""