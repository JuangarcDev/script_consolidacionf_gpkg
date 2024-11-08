tables = [
    {
        'table_base': 'lc_predio',
        'table_src': 'lc_predio',
        'table_target': 'gc_predio',
        'domains':[
            {'column_name':'condicion_predio', 'table_gc_name':'gc_condicionprediotipo'},
            {'column_name':'destinacion_economica', 'table_gc_name':'gc_destinacioneconomicatipo'},
            {'column_name':'clase_suelo', 'table_gc_name':'gc_clasesuelotipo'},
            {'column_name':'categoria_suelo', 'table_gc_name':'gc_categoriasuelotipo'},
            {'column_name':'tipo', 'table_gc_name':'gc_prediotipo'},
        ]
    },
    {
        'table_base': 'extdireccion',
        'table_src': 'extdireccion',
        'table_target': 'extdireccion',
        'domains':[
            {'column_name':'clase_via_principal', 'table_gc_name':'extdireccion_clase_via_principal'},
            {'column_name':'sector_ciudad', 'table_gc_name':'extdireccion_sector_ciudad'},
            {'column_name':'sector_predio', 'table_gc_name':'extdireccion_sector_predio'},
            {'column_name':'tipo_direccion', 'table_gc_name':'extdireccion_tipo_direccion'},
        ]
    },
    {
        'table_base': 'lc_predio',
        'table_src': 'extavaluo',
        'table_target': 'extavaluo',
        'domains':[]
    },
    {
        'table_base': 'lc_predio',
        'table_src': 'extvalor',
        'table_target': 'extvalor',
        'domains':[
            {'column_name':'tipo', 'table_gc_name':'gc_valortipo'},
        ]
    },
    {
        'table_base': 'lc_interesado',
        'table_src': 'lc_interesado',
        'table_target': 'gc_interesado',
        'domains':[
            {'column_name':'estado_civil', 'table_gc_name':'gc_estadociviltipo'},
            {'column_name':'grupo_etnico', 'table_gc_name':'gc_grupoetnicotipo'},
            {'column_name':'sexo', 'table_gc_name':'gc_sexotipo'},
            {'column_name':'tipo', 'table_gc_name':'gc_interesadotipo'},
            {'column_name':'tipo_documento', 'table_gc_name':'gc_interesadodocumentotipo'},
            {'column_name':'verificado', 'table_gc_name':'gc_verificaciontipo'},
        ]
    },
    {
        'table_base': 'lc_agrupacioninteresados',
        'table_src': 'lc_agrupacioninteresados',
        'table_target': 'gc_agrupacioninteresados',
        'domains':[
            {'column_name':'tipo', 'table_gc_name':'col_grupointeresadotipo'},
        ]
    },
    {
        'table_base': 'col_miembros',
        'table_src': 'col_miembros',
        'table_target': 'col_miembros',
        'domains':[]
    },
    {
        'table_base': 'lc_derecho',
        'table_src': 'lc_derecho',
        'table_target': 'gc_derecho',
        'domains':[
            {'column_name':'tipo', 'table_gc_name':'gc_derechotipo'},
        ]
    },
    {
        'table_base': 'lc_terreno',
        'table_src': 'lc_terreno',
        'table_target': 'gc_terreno',
        'domains':[]
    },
    {
        'table_base': 'lc_construccion',
        'table_src': 'lc_construccion',
        'table_target': 'gc_construccion',
        'domains':[
            {'column_name':'tipo_construccion', 'table_gc_name':'gc_construcciontipo'},
            {'column_name':'tipo_dominio', 'table_gc_name':'gc_dominioconstrucciontipo'},
        ]
    },
    {
        'table_base': 'lc_caracteristicasunidadconstruccion',
        'table_src': 'lc_caracteristicasunidadconstruccion',
        'table_target': 'gc_caracteristicasunidadconstruccion',
        'domains':[
            {'column_name':'tipo_construccion', 'table_gc_name':'gc_construcciontipo'},
            {'column_name':'tipo_dominio', 'table_gc_name':'gc_dominioconstrucciontipo'},
            {'column_name':'tipo_planta', 'table_gc_name':'gc_construccionplantatipo'},
            {'column_name':'tipo_unidad_construccion', 'table_gc_name':'gc_unidadconstrucciontipo'},
            {'column_name':'uso', 'table_gc_name':'gc_usouconstipo'},
        ]
    },
    {
        'table_base': 'lc_servidumbretransito',
        'table_src': 'lc_servidumbretransito',
        'table_target': 'gc_servidumbretransito',
        'domains':[]
    },
    {
        'table_base': 'lc_unidadconstruccion',
        'table_src': 'lc_unidadconstruccion',
        'table_target': 'gc_unidadconstruccion',
        'domains':[]
    },

    {
        'table_base': 'col_uebaunit',
        'table_src': 'col_uebaunit',
        'table_target': 'col_uebaunit',
        'domains':[]
    },
    {
        'table_base': 'lc_puntolindero',
        'table_src': 'lc_puntolindero',
        'table_target': 'gc_puntolindero',
        'domains':[
            {'column_name':'acuerdo', 'table_gc_name':'gc_acuerdotipo'},
            {'column_name':'fotoidentificacion', 'table_gc_name':'gc_fotoidentificaciontipo'},
            {'column_name':'metodo_produccion', 'table_gc_name':'col_metodoproducciontipo'},
            {'column_name':'punto_tipo', 'table_gc_name':'gc_puntotipo'},
        ]
    },
    {
        'table_base': 'lc_lindero',
        'table_src': 'lc_lindero',
        'table_target': 'gc_lindero',
        'domains':[]
    },
    {
        'table_base': 'col_puntoccl',
        'table_src': 'col_puntoccl',
        'table_target': 'col_puntoccl',
        'domains':[]
    },
    {
        'table_base': 'col_masccl',
        'table_src': 'col_masccl',
        'table_target': 'col_masccl',
        'domains':[]
    },
    {
        'table_base': 'col_menosccl',
        'table_src': 'col_menosccl',
        'table_target': 'col_menosccl',
        'domains':[]
    },
    {
        'table_base': 'lc_fuenteadministrativa',
        'table_src': 'lc_fuenteadministrativa',
        'table_target': 'gc_fuenteadministrativa',
        'domains':[
            {'column_name':'estado_disponibilidad', 'table_gc_name':'col_estadodisponibilidadtipo'},
            {'column_name':'tipo', 'table_gc_name':'gc_fuenteadministrativatipo'},
        ]
    },
    {
        'table_base': 'lc_fuenteespacial',
        'table_src': 'lc_fuenteespacial',
        'table_target': 'gc_fuenteespacial',
        'domains':[
            {'column_name':'estado_disponibilidad', 'table_gc_name':'col_estadodisponibilidadtipo'},
            {'column_name':'tipo', 'table_gc_name':'gc_fuenteespacialtipo'}
        ]
    },
    {
        'table_base': 'extarchivo',
        'table_src': 'extarchivo',
        'table_target': 'extarchivo',
        'domains':[]
    },
    {
        'table_base': 'col_rrrfuente',
        'table_src': 'col_rrrfuente',
        'table_target': 'col_rrrfuente',
        'domains':[]
    },
    {
        'table_base': 'extreferenciaregistralsistemaantiguo',
        'table_src': 'extreferenciaregistralsistemaantiguo',
        'table_target': 'extreferenciaregistralsistemaantiguo',
        'domains':[
            {'column_name':'tipo_referencia', 'table_gc_name':'extreferenciaregistralsistemaantiguo_tipo_referencia'},
        ]
    },
    {
        'table_base': 'lc_calificacionnoconvencional',
        'table_src': 'lc_calificacionnoconvencional',
        'table_target': 'cuc_calificacionnoconvencional',
        'domains':[
            {'column_name':'tipo_anexo', 'table_gc_name':'cuc_anexotipo'},
        ]
    },
    {
        'table_base': 'lc_datosphcondominio',
        'table_src': 'lc_datosphcondominio',
        'table_target': 'gc_datosphcondominio',
        'domains':[]
    },
    {
        'table_base': 'lc_tipologiaconstruccion',
        'table_src': 'lc_tipologiaconstruccion',
        'table_target': 'cuc_tipologiaconstruccion',
        'domains':[
            {'column_name':'tipo_tipologia', 'table_gc_name':'cuc_tipologiatipo'},
        ]
    },
    {
        'table_base': 'lc_predio_copropiedad',
        'table_src': 'lc_predio_copropiedad',
        'table_target': 'gc_prediocopropiedad',
        'domains':[]
    },
    {
        'table_base': 'lc_predio',
        'table_src': 'extmatriculainmobiliaria',
        'table_target': 'extmatriculainmobiliaria',
        'domains':[
            {'column_name':'tipo', 'table_gc_name':'gc_matriculainmobiliariatipo'},
        ]
    },
    {
        'table_base': 'av_zonahomogeneafisicarural',
        'table_src': 'av_zonahomogeneafisicarural',
        'table_target': 'zhf_rural',
        'domains':[]
    },
    {
        'table_base': 'av_zonahomogeneafisicaurbana',
        'table_src': 'av_zonahomogeneafisicaurbana',
        'table_target': 'zhf_urbana',
        'domains':[]
    },
    {
        'table_base': 'av_zonahomogeneageoeconomicarural',
        'table_src': 'av_zonahomogeneageoeconomicarural',
        'table_target': 'zhg_rural',
        'domains':[]
    },
    {
        'table_base': 'av_zonahomogeneageoeconomicaurbana',
        'table_src': 'av_zonahomogeneageoeconomicaurbana',
        'table_target': 'zhg_urbana',
        'domains':[]
    },
    {
        'table_base': 'cc_manzana',
        'table_src': 'cc_manzana',
        'table_target': 'cc_manzana',
        'domains':[]
    },
    {
        'table_base': 'cc_perimetrourbano',
        'table_src': 'cc_perimetrourbano',
        'table_target': 'cc_perimetrourbano',
        'domains':[]
    },
    {
        'table_base': 'cc_sectorrural',
        'table_src': 'cc_sectorrural',
        'table_target': 'cc_sectorrural',
        'domains':[]
    },
    {
        'table_base': 'cc_sectorurbano',
        'table_src': 'cc_sectorurbano',
        'table_target': 'cc_sectorurbano',
        'domains':[]
    },
    {
        'table_base': 'cc_vereda',
        'table_src': 'cc_vereda',
        'table_target': 'cc_vereda',
        'domains':[]
    },
    {
        'table_base':   'col_uefuente',
        'table_src':    'col_uefuente',
        'table_target': 'col_uefuente',
        'domains':[]
    },
    {
        'table_base':   'lc_predio_informalidad',
        'table_src':    'lc_predio_informalidad',
        'table_target': 'gc_predio_informalidad',
        'domains':[]
    },
    {
        'table_base':   'lc_puntolevantamiento',
        'table_src':    'lc_puntolevantamiento',
        'table_target': 'gc_puntolevantamiento',
        'domains':[
            {'column_name':'fotoidentificacion', 'table_gc_name':'gc_fotoidentificaciontipo'},
            {'column_name':'punto_tipo', 'table_gc_name':'gc_puntotipo'},
            {'column_name':'metodo_produccion', 'table_gc_name':'col_metodoproducciontipo'},
            {'column_name':'tipo_punto_levantamiento', 'table_gc_name':'gc_puntolevtipo'},
        ]
    },
    {
        'table_base':   'cc_limitemunicipio',
        'table_src':    'cc_limitemunicipio',
        'table_target': 'cc_limitemunicipio',
        'domains':[]
    },
    {
        'table_base':   'lc_datosadicionaleslevantamientocatastral',
        'table_src':    'lc_datosadicionaleslevantamientocatastral',
        'table_target': 'dlc_datosadicionaleslevantamientocatastral',
        'domains':[]
    },
    {
        'table_base':   'lc_ofertasmercadoinmobiliario',
        'table_src':    'lc_ofertasmercadoinmobiliario',
        'table_target': 'om_ofertasmercadoinmobiliario',
        'domains':[]
    },



    {
        'table_base':   'cc_barrio',
        'table_src':    'cc_barrio',
        'table_target': 'cc_barrio',
        'domains':[]
    },
    {
        'table_base':   'cc_centropoblado',
        'table_src':    'cc_centropoblado',
        'table_target': 'cc_centropoblado',
        'domains':[]
    },
    {
        'table_base':   'cc_corregimiento',
        'table_src':    'cc_corregimiento',
        'table_target': 'cc_corregimiento',
        'domains':[]
    },
    {
        'table_base':   'cc_localidadcomuna',
        'table_src':    'cc_localidadcomuna',
        'table_target': 'cc_localidadcomuna',
        'domains':[]
    },
    {
        'table_base':   'cc_nomenclaturavial',
        'table_src':    'cc_nomenclaturavial',
        'table_target': 'cc_nomenclaturavial',
        'domains':[
            {'column_name':'tipo_via', 'table_gc_name':'cc_nomenclaturavial_tipo_via'}
        ]
    },
    {
        'table_base':   'col_baunitfuente',
        'table_src':    'col_baunitfuente',
        'table_target': 'col_baunitfuente',
        'domains':[]
    },
    {
        'table_base':   'col_cclfuente',
        'table_src':    'col_cclfuente',
        'table_target': 'col_cclfuente',
        'domains':[]
    },
    {
        'table_base':   'col_puntofuente',
        'table_src':    'col_puntofuente',
        'table_target': 'col_puntofuente',
        'domains':[]
    },
    {
        'table_base':   'lc_calificacionconvencional',
        'table_src':    'lc_calificacionconvencional',
        'table_target': 'cuc_calificacionconvencional',
        'domains':[
            {'column_name':'tipo_calificar', 'table_gc_name':'cuc_calificartipo'}
        ]   
    },
    {
        'table_base':   'lc_grupocalificacion',
        'table_src':    'lc_grupocalificacion',
        'table_target': 'cuc_grupocalificacion',
        'domains':[
            {'column_name':'clase_calificacion', 'table_gc_name':'cuc_clasecalificaciontipo'},
            {'column_name':'conservacion', 'table_gc_name':'cuc_estadoconservaciontipo'}
        ]   
    },
    {
        'table_base':   'lc_objetoconstruccion',
        'table_src':    'lc_objetoconstruccion',
        'table_target': 'cuc_objetoconstruccion',
        'domains':[
            {'column_name':'tipo_objeto_construccion', 'table_gc_name':'cuc_objetoconstrucciontipo'}
        ]
    },
    {
        'table_base':   '',
        'table_src':    '',
        'table_target': '',
        'domains':[]
    },
    {
        'table_base':   '',
        'table_src':    '',
        'table_target': '',
        'domains':[]
    },
    {
        'table_base':   '',
        'table_src':    '',
        'table_target': '',
        'domains':[]
    }
]