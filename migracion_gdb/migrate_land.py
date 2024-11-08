from dictionary_actualization import *

def execute_query(conn, cursor, query):
    cursor.execute(query)
    conn.commit()

def get_results(conn, cursor, query, type='all'):
    execute_query(conn, cursor, query)
    if type == 'one':
        return cursor.fetchone()
    else:
        return cursor.fetchall()

def insert_statement(tuple, type_dictionary):
    result = ""
    type_dictionary_names = list(type_dictionary)
    for index in range(len(tuple)):
        type = type_dictionary[type_dictionary_names[index]]
        if tuple[index] == None:
            result += "null"
        elif type == 'string':
            result += "'"+str(tuple[index])+"'"
        elif type == 'date':
            result += "'"+str(tuple[index])+"'"
        else:
            result += "'"+str(tuple[index])+"'"
        result += ','
    return result[:-1]

def check_obj(obj, msg_error='', raise_error=False):
    if obj is None or (obj is not None and len(obj) == 0):
        if msg_error != '':
            print(msg_error)
        if raise_error:
            raise Exception(msg_error)
        else:
            return False
    return True

def migrate_land(conn_src, cursor_src, conn_target, cursor_target, schema_src, schema_target, land_src_id, dict_parties, dict_buildingunitchar, dict_building, dict_buildingunit,withGeom=True):
    # Migrate land data
    query = "select "+','.join(land_attributes)+" from \""+schema_src+"\".gc_predio \
        where id=%d" % land_src_id
    land_obj = get_results(conn_src, cursor_src, query, type='one')
    check_obj(land_obj, msg_error='Este predio no existe en la fuente: %d' % land_src_id, raise_error=True)
    query = "insert into \""+schema_target+"\".gc_predio ("+','.join(land_attributes)+") values \
        ("+insert_statement(land_obj,land_attributes_types)+") returning id;"
    land_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
    ## Migrate extaddress
    query = "select id from \""+schema_src+"\".extdireccion \
        where gc_predio_direccion = %d" % land_src_id
    extdireccion_src_ids = get_results(conn_src, cursor_src, query)
    for extdireccion_src_id in extdireccion_src_ids:
        query = "select "+','.join(address_attributes)+" from \""+schema_src+"\".extdireccion \
            where id = %d" % extdireccion_src_id
        extaddress_obj = get_results(conn_src, cursor_src, query, type='one')
        extaddress_obj_ed = list(extaddress_obj)
        extaddress_obj_ed[address_attributes.index('gc_predio_direccion')] = land_target_id
        query = "insert into \""+schema_target+"\".extdireccion ("+','.join(address_attributes)+") values \
            ("+insert_statement(extaddress_obj_ed,address_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate phdata
    query = "select id from \""+schema_src+"\".gc_datosphcondominio \
        where gc_predio = %d" % land_src_id
    phdata_src_ids = get_results(conn_src, cursor_src, query)
    for phdata_src_id in phdata_src_ids:
        query = "select "+','.join(phdata_attributes)+" from \""+schema_src+"\".gc_datosphcondominio \
            where id = %d" % phdata_src_id
        phdata_obj = get_results(conn_src, cursor_src, query, type='one')
        phdata_obj_ed = list(phdata_obj)
        phdata_obj_ed[phdata_attributes.index('gc_predio')] = land_target_id
        query = "insert into \""+schema_target+"\".gc_datosphcondominio ("+','.join(phdata_attributes)+") values \
            ("+insert_statement(phdata_obj_ed,phdata_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate valuations
    query = "select id from \""+schema_src+"\".extavaluo \
        where gc_predio_avaluo = %d" % land_src_id
    extvaluation_src_ids = get_results(conn_src, cursor_src, query)
    for extvaluation_src_id in extvaluation_src_ids:
        query = "select "+','.join(valuation_attributes)+" from \""+schema_src+"\".extavaluo \
            where id = %d" % extvaluation_src_id
        extvaluation_obj = get_results(conn_src, cursor_src, query, type='one')
        extvaluation_obj_ed = list(extvaluation_obj)
        extvaluation_obj_ed[valuation_attributes.index('gc_predio_avaluo')] = land_target_id
        query = "insert into \""+schema_target+"\".extavaluo ("+','.join(valuation_attributes)+") values \
            ("+insert_statement(extvaluation_obj_ed,valuation_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate extvalue
    query = "select "+','.join(extvalue_attributes)+" from \""+schema_src+"\".extvalor where gc_predio_valor_referencia = "+str(land_src_id)
    extvalue_obj_list = get_results(conn_src, cursor_src, query)
    for extvalue_obj in extvalue_obj_list:
        extvalue_obj_ed = list(extvalue_obj)
        extvalue_obj_ed[extvalue_attributes.index('gc_predio_valor_referencia')] = land_target_id
        query = "insert into \""+schema_target+"\".extvalor ("+','.join(extvalue_attributes)+") values \
            ("+insert_statement(extvalue_obj_ed,extvalue_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate right
    query = "select "+','.join(rigth_attributes)+" from \""+schema_src+"\".gc_derecho where baunit = "+str(land_src_id)
    right_src_obj_list = get_results(conn_src, cursor_src, query)
    for right_src_obj in right_src_obj_list:
        right_src_obj_ed = list(right_src_obj)
        right_src_obj_ed[rigth_attributes.index('baunit')]=land_target_id
        right_src_obj_ed[rigth_attributes.index('interesado_gc_interesado')]=None
        right_src_obj_ed[rigth_attributes.index('interesado_gc_agrupacioninteresados')]=None
        query = "insert into \""+schema_target+"\".gc_derecho ("+','.join(rigth_attributes)+") values \
            ("+insert_statement(right_src_obj_ed,rigth_attributes_types)+") returning id;"
        right_target_id = get_results(conn_target,cursor_target,query, type='one')[0]
        ## Migrate external land sources
        query = "select fuente_administrativa from \""+schema_src+"\".col_rrrfuente where rrr_gc_derecho in (select id from \""+schema_src+"\".gc_derecho where baunit =  "+str(land_src_id)+")"
        ext_admin_source_src_ids = get_results(conn_src, cursor_src, query)
        if check_obj(ext_admin_source_src_ids, msg_error='No existen fuentes administrativas externas del predio de la fuente fuente: %d' % land_src_id, raise_error=False):
            for ext_admin_source_src_id in ext_admin_source_src_ids:
                query = "select "+','.join(adminsource_attributes)+" from \""+schema_src+"\".gc_fuenteadministrativa \
                    where id = %d" % ext_admin_source_src_id
                admin_source_obj = get_results(conn_src, cursor_src, query, type='one')
                check_obj(admin_source_obj, msg_error='La fuente administrativa no existe en la fuente: %d' % ext_admin_source_src_id, raise_error=True)
                query = "insert into \""+schema_target+"\".gc_fuenteadministrativa ("+','.join(adminsource_attributes)+") values \
                    ("+insert_statement(admin_source_obj,adminsource_attributes_types)+") returning id;"
                admin_source_target_id = get_results(conn_target,cursor_target,query,type='one')[0]
                colrrrr_target_obj_ed = [None for i in range(len(colrrrsource_attributes))]
                colrrrr_target_obj_ed[colrrrsource_attributes.index('fuente_administrativa')] = admin_source_target_id
                colrrrr_target_obj_ed[colrrrsource_attributes.index('rrr_gc_derecho')] = right_target_id
                query = "insert into \""+schema_target+"\".col_rrrfuente ("+','.join(colrrrsource_attributes)+") values \
                    ("+insert_statement(colrrrr_target_obj_ed,colrrrsource_attributes_types)+");"
                execute_query(conn_target,cursor_target,query)
        ## Migrate parties
        if right_src_obj[rigth_attributes.index('interesado_gc_interesado')] != None:
            party_src_id = right_src_obj[rigth_attributes.index('interesado_gc_interesado')]
            if party_src_id in dict_parties:
                party_target_id = dict_parties[party_src_id]
            else:
                query = "select "+','.join(party_attributes)+" from \""+schema_src+"\".gc_interesado where id = "+str(party_src_id)
                party_src_obj = get_results(conn_src, cursor_src, query, type='one')
                query = "insert into \""+schema_target+"\".gc_interesado ("+','.join(party_attributes)+") values \
                    ("+insert_statement(party_src_obj,party_attributes_types)+") returning id;"
                party_target_id = get_results(conn_target,cursor_target,query,type='one')[0]
                dict_parties[party_src_id] = party_target_id
            query="update \""+schema_target+"\".gc_derecho set interesado_gc_interesado="+str(party_target_id)+" where id="+str(right_target_id)
            execute_query(conn_target,cursor_target,query)
        else:
            group_party_src_id = right_src_obj[rigth_attributes.index('interesado_gc_agrupacioninteresados')]
            query = "select "+','.join(groupparty_attributes)+" from \""+schema_src+"\".gc_agrupacioninteresados where id = "+str(group_party_src_id)
            groupparty_src_obj = get_results(conn_src,cursor_src,query,type='one')
            query = "insert into \""+schema_target+"\".gc_agrupacioninteresados ("+','.join(groupparty_attributes)+") values \
                ("+insert_statement(groupparty_src_obj,groupparty_attributes_types)+") returning id;"
            groupparty_target_id = get_results(conn_target,cursor_target,query, type='one')[0]
            query = "select interesado_gc_interesado from \""+schema_src+"\".col_miembros where agrupacion = "+str(group_party_src_id)
            parties_src_id = get_results(conn_src,cursor_src,query)
            for party_src_id in parties_src_id:
                party_src_id = party_src_id[0]
                if party_src_id in dict_parties:
                    party_target_id = dict_parties[party_src_id]
                else:
                    query = "select "+','.join(party_attributes)+" from \""+schema_src+"\".gc_interesado where id = "+str(party_src_id)
                    party_src_obj = get_results(conn_src, cursor_src, query, type='one')
                    query = "insert into \""+schema_target+"\".gc_interesado ("+','.join(party_attributes)+") values \
                        ("+insert_statement(party_src_obj,party_attributes_types)+") returning id;"
                    party_target_id = get_results(conn_target,cursor_target,query,type='one')[0]
                    dict_parties[party_src_id] = party_target_id
                colmembers_obj_ed = [None for i in range(len(colmembers_attributes))]
                colmembers_obj_ed[colmembers_attributes.index('interesado_gc_interesado')] = party_target_id
                colmembers_obj_ed[colmembers_attributes.index('agrupacion')] = groupparty_target_id
                query = "insert into \""+schema_target+"\".col_miembros ("+','.join(colmembers_attributes)+") values \
                    ("+insert_statement(colmembers_obj_ed,colmembers_attributes_types)+");"
                execute_query(conn_target,cursor_target,query)
            query="update \""+schema_target+"\".gc_derecho set interesado_gc_agrupacioninteresados="+str(groupparty_target_id)+" where id="+str(right_target_id)
            execute_query(conn_target,cursor_target,query)
    ## Migrate internal land sources
    query = "select fuente_administrativa from \""+schema_src+"\".col_unidadfuente where unidad = %d" % land_src_id
    int_admin_source_src_ids = get_results(conn_src, cursor_src, query)
    if check_obj(int_admin_source_src_ids, msg_error='No existen fuentes administrativas internas del predio de la fuente fuente: %d' % land_src_id, raise_error=False):
        for int_admin_source_src_id in int_admin_source_src_ids:
            query = "select "+','.join(adminsource_attributes)+" from \""+schema_src+"\".gc_fuenteadministrativa \
                where id = %d" % int_admin_source_src_id
            admin_source_obj = get_results(conn_src, cursor_src, query, type='one')
            check_obj(admin_source_obj, msg_error='La fuente administrativa no existe en la fuente: %d' % int_admin_source_src_id, raise_error=True)
            query = "insert into \""+schema_target+"\".gc_fuenteadministrativa ("+','.join(adminsource_attributes)+") values \
                ("+insert_statement(admin_source_obj,adminsource_attributes_types)+") returning id;"
            admin_source_target_id = get_results(conn_target,cursor_target,query,type='one')[0]
            colunitsource_target_obj_ed = [None for i in range(len(colunitsource_attributes))]
            colunitsource_target_obj_ed[colunitsource_attributes.index('fuente_administrativa')] = admin_source_target_id
            colunitsource_target_obj_ed[colunitsource_attributes.index('unidad')] = land_target_id
            query = "insert into \""+schema_target+"\".col_unidadfuente ("+','.join(colunitsource_attributes)+") values \
                ("+insert_statement(colunitsource_target_obj_ed,colunitsource_attributes_types)+") returning id;"
            execute_query(conn_target,cursor_target,query)    
    ## Migrate extalerts
    query = "select "+','.join(extalert_attributes)+" from \""+schema_src+"\".extalertas where gc_predio_alerta = "+str(land_src_id)
    extalert_obj_list = get_results(conn_src, cursor_src, query)
    for extalert_obj in extalert_obj_list:
        extalert_obj_ed = list(extalert_obj)
        extalert_obj_ed[extalert_attributes.index('gc_predio_alerta')] = land_target_id
        query = "insert into \""+schema_target+"\".extalertas ("+','.join(extalert_attributes)+") values \
            ("+insert_statement(extalert_obj_ed,extalert_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate lc_extradata
    query = "select "+','.join(extradata_attributes)+" from \""+schema_src+"\".dlc_datosadicionaleslevantamientocatastral where gc_predio = "+str(land_src_id)
    extradata_obj_list = get_results(conn_src, cursor_src, query)
    for extradata_obj in extradata_obj_list:
        extradata_obj_ed = list(extradata_obj)
        extradata_obj_ed[extradata_attributes.index('gc_predio')] = land_target_id
        if extradata_obj_ed[extradata_attributes.index('observaciones')] is not None:
            extradata_obj_ed[extradata_attributes.index('observaciones')] = extradata_obj_ed[extradata_attributes.index('observaciones')].replace("'", "")
        query = "insert into \""+schema_target+"\".dlc_datosadicionaleslevantamientocatastral ("+','.join(extradata_attributes)+") values \
            ("+insert_statement(extradata_obj_ed,extradata_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate extrealestateregistration
    query = "select "+','.join(extrealestateregistration_attributes)+" from \""+schema_src+"\".extmatriculainmobiliaria where gc_predio_matricula_matriz_derivada = "+str(land_src_id)
    extrealestateregistration_obj_list = get_results(conn_src, cursor_src, query)
    for extrealestateregistration_obj in extrealestateregistration_obj_list:
        extrealestateregistration_obj_ed = list(extrealestateregistration_obj)
        extrealestateregistration_obj_ed[extrealestateregistration_attributes.index('gc_predio_matricula_matriz_derivada')] = land_target_id
        query = "insert into \""+schema_target+"\".extmatriculainmobiliaria ("+','.join(extrealestateregistration_attributes)+") values \
            ("+insert_statement(extrealestateregistration_obj_ed,extrealestateregistration_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate extregistryreferenceoldsystem
    query = "select "+','.join(extregistryreferenceoldsystem_attributes)+" from \""+schema_src+"\".extreferenciaregistralsistemaantiguo where gc_predio_referencia_registral_sistema_antiguo = "+str(land_src_id)
    extregistryreferenceoldsystem_obj_list = get_results(conn_src, cursor_src, query)
    for extregistryreferenceoldsystem_obj in extregistryreferenceoldsystem_obj_list:
        extregistryreferenceoldsystem_obj_ed = list(extregistryreferenceoldsystem_obj)
        extregistryreferenceoldsystem_obj_ed[extregistryreferenceoldsystem_attributes.index('gc_predio_referencia_registral_sistema_antiguo')] = land_target_id
        query = "insert into \""+schema_target+"\".extreferenciaregistralsistemaantiguo ("+','.join(extregistryreferenceoldsystem_attributes)+") values \
            ("+insert_statement(extregistryreferenceoldsystem_obj_ed,extregistryreferenceoldsystem_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    ## Migrate realestatemarketoffers
    query = "select "+','.join(realestatemarketoffers_attributes)+" from \""+schema_src+"\".om_ofertasmercadoinmobiliario where gc_predio = "+str(land_src_id)
    realestatemarketoffers_obj_list = get_results(conn_src, cursor_src, query)
    for realestatemarketoffers_obj in realestatemarketoffers_obj_list:
        realestatemarketoffers_obj_ed = list(realestatemarketoffers_obj)
        realestatemarketoffers_obj_ed[realestatemarketoffers_attributes.index('gc_predio')] = land_target_id
        query = "insert into \""+schema_target+"\".om_ofertasmercadoinmobiliario ("+','.join(realestatemarketoffers_attributes)+") values \
            ("+insert_statement(realestatemarketoffers_obj_ed,realestatemarketoffers_attributes_types)+");"
        execute_query(conn_target,cursor_target,query)
    # Migrate Terrain related data
    # Get terrain_id
    if withGeom:
        query = "select ue_gc_terreno from \""+schema_src+"\".col_uebaunit where unidad=" + str(land_src_id) + " and ue_gc_terreno is not null"
        terrain_src_id = get_results(conn_src, cursor_src, query, type='one')
        if check_obj(terrain_src_id,'El predio no tiene terreno %s' % land_src_id,raise_error=False):
            terrain_src_id = terrain_src_id[0]
            ## Migrate terrain
            query = "select "+','.join(terrain_attributes)+" from \""+schema_src+"\".gc_terreno where id = "+str(terrain_src_id)
            terrain_obj = get_results(conn_src, cursor_src, query, type='one')
            query = "insert into \""+schema_target+"\".gc_terreno ("+','.join(terrain_attributes)+") values \
                ("+insert_statement(terrain_obj,terrain_attributes_types)+") returning id;"
            terrain_target_id = get_results(conn_target,cursor_target,query, type='one')[0]
            ## Migrate col_uebaunit
            col_uebaunit_target_obj_ed = [None for i in range(len(col_uebaunit_attributes))]
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('ue_gc_terreno')] = terrain_target_id
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('unidad')] = land_target_id
            query = "insert into \""+schema_target+"\".col_uebaunit ("+','.join(col_uebaunit_attributes)+") values \
                ("+insert_statement(col_uebaunit_target_obj_ed,col_uebaunit_attributes_types)+");"
            execute_query(conn_target, cursor_target, query)
        # Migrate building
        query = "select ue_gc_construccion from \""+schema_src+"\".col_uebaunit where unidad = '"+str(land_src_id)+"' and ue_gc_construccion is not null;"
        building_src_ids = get_results(conn_src, cursor_src, query)
        for building_src_id in building_src_ids:
            building_src_id = building_src_id[0]
            if building_src_id in dict_building:
                building_target_id = dict_building[building_src_id]
            else:
                query = "select "+','.join(building_attributes)+" from \""+schema_src+"\".gc_construccion \
                    where id = %d" % building_src_id
                building_obj = get_results(conn_src, cursor_src, query, type='one')
                check_obj(building_obj, msg_error='Esta construcción no existe en la fuente: %d' % building_src_id, raise_error=True)
                query = "insert into \""+schema_target+"\".gc_construccion ("+','.join(building_attributes)+") values \
                    ("+insert_statement(building_obj,building_attributes_types)+") returning id;"
                building_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
                dict_building[building_src_id] = building_target_id
            col_uebaunit_target_obj_ed = [None for i in range(len(col_uebaunit_attributes))]
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('ue_gc_construccion')] = building_target_id
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('unidad')] = land_target_id
            query = "insert into \""+schema_target+"\".col_uebaunit ("+','.join(col_uebaunit_attributes)+") values \
                ("+insert_statement(col_uebaunit_target_obj_ed,col_uebaunit_attributes_types)+");"
            execute_query(conn_target, cursor_target, query)
            # Migrate building unit
            query = "select id from \""+schema_src+"\".gc_unidadconstruccion where gc_construccion = "+str(building_src_id)+" and gc_construccion is not null;"
            buildingunit_src_ids = get_results(conn_src, cursor_src, query)
            for buildingunit_src_id in buildingunit_src_ids:
                buildingunit_src_id = buildingunit_src_id[0]
                if buildingunit_src_id in dict_buildingunit:
                    buildingunit_target_id = dict_buildingunit[buildingunit_src_id]
                else:
                    query = "select "+','.join(buildingunit_attributes)+" from \""+schema_src+"\".gc_unidadconstruccion \
                        where id = %d" % buildingunit_src_id
                    buildingunit_obj = get_results(conn_src, cursor_src, query, type='one')
                    check_obj(buildingunit_obj, msg_error='Esta unidad de construcción no existe en la fuente: %d' % buildingunit_src_id, raise_error=True)
                    buildingunitchar_src_id = buildingunit_obj[buildingunit_attributes.index('gc_caracteristicasunidadconstruccion')]
                    if buildingunitchar_src_id in dict_buildingunitchar:
                        buildingunitchar_target_id = dict_buildingunitchar[buildingunitchar_src_id]
                    else:
                        query = "select "+','.join(buildingunitchar_attributes)+" from \""+schema_src+"\".gc_caracteristicasunidadconstruccion \
                            where id = %d" % buildingunitchar_src_id
                        buildingunitchar_obj = get_results(conn_src, cursor_src, query, type='one')
                        query = "insert into \""+schema_target+"\".gc_caracteristicasunidadconstruccion ("+','.join(buildingunitchar_attributes)+") values \
                            ("+insert_statement(buildingunitchar_obj,buildingunitchar_attributes_types)+") returning id;"
                        buildingunitchar_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
                        dict_buildingunitchar[buildingunitchar_src_id] = buildingunitchar_target_id
                        #################################
                        query = "select id from \""+schema_src+"\".cuc_tipologiaconstruccion where gc_caracteristicasunidadconstruccion = '"+str(buildingunitchar_src_id)+"';"
                        tipology_src_ids = get_results(conn_src, cursor_src, query)
                        for tipology_src_id in tipology_src_ids:
                            tipology_src_id = tipology_src_id[0]
                            query = "select "+','.join(buildingtypology_attributes)+" from \""+schema_src+"\".cuc_tipologiaconstruccion where id = %d" % tipology_src_id
                            tipology_obj = get_results(conn_src, cursor_src, query, type='one')
                            check_obj(tipology_obj, msg_error='Esta tipologia no existe en la fuente: %d' % tipology_src_id, raise_error=True)
                            tipology_obj_ed = list(tipology_obj)
                            tipology_obj_ed[buildingtypology_attributes.index('gc_caracteristicasunidadconstruccion')] = buildingunitchar_target_id
                            query = "insert into \""+schema_target+"\".cuc_tipologiaconstruccion ("+','.join(buildingtypology_attributes)+") values \
                                ("+insert_statement(tipology_obj_ed,buildingtypology_attributes_types)+") returning id;"
                            execute_query(conn_target, cursor_target, query)
                        #################################
                        query = "select id from \""+schema_src+"\".cuc_calificacionnoconvencional where gc_caracteristicasunidadconstruccion = '"+str(buildingunitchar_src_id)+"';"
                        nonconventional_src_ids = get_results(conn_src, cursor_src, query)
                        for nonconventional_src_id in nonconventional_src_ids:
                            nonconventional_src_id = nonconventional_src_id[0]
                            query = "select "+','.join(nonconventionalcalification_attributes)+" from \""+schema_src+"\".cuc_calificacionnoconvencional where id = %d" % nonconventional_src_id
                            nonconventional_obj = get_results(conn_src, cursor_src, query, type='one')
                            check_obj(nonconventional_obj, msg_error='Esta calificación no convencional no existe en la fuente: %d' % nonconventional_src_id, raise_error=True)
                            nonconventional_obj_ed = list(nonconventional_obj)
                            nonconventional_obj_ed[nonconventionalcalification_attributes.index('gc_caracteristicasunidadconstruccion')] = buildingunitchar_target_id
                            query = "insert into \""+schema_target+"\".cuc_calificacionnoconvencional ("+','.join(nonconventionalcalification_attributes)+") values \
                                ("+insert_statement(nonconventional_obj_ed,nonconventionalcalification_attributes_types)+") returning id;"
                            execute_query(conn_target, cursor_target, query)
                        #################################
                    buildingunit_obj_ed = list(buildingunit_obj)
                    buildingunit_obj_ed[buildingunit_attributes.index('gc_caracteristicasunidadconstruccion')] = buildingunitchar_target_id
                    buildingunit_obj_ed[buildingunit_attributes.index('gc_construccion')] = building_target_id
                    query = "insert into \""+schema_target+"\".gc_unidadconstruccion ("+','.join(buildingunit_attributes)+") values \
                        ("+insert_statement(buildingunit_obj_ed,buildingunit_attributes_types)+") returning id;"
                    buildingunit_target_id = get_results(conn_target,cursor_target,query, type='one')[0]
                    dict_buildingunit[buildingunit_src_id] = buildingunit_target_id
        # Migrate simple building unit
        query = "select ue_gc_unidadconstruccion from \""+schema_src+"\".col_uebaunit where unidad = '"+str(land_src_id)+"' and ue_gc_unidadconstruccion is not null;"
        buildingunit_src_ids = get_results(conn_src, cursor_src, query)
        for buildingunit_src_id in buildingunit_src_ids:
            buildingunit_src_id = buildingunit_src_id[0]
            query = "select "+','.join(buildingunit_attributes)+" from \""+schema_src+"\".gc_unidadconstruccion \
                where id = %d" % buildingunit_src_id
            buildingunit_obj = get_results(conn_src, cursor_src, query, type='one')
            check_obj(buildingunit_obj, msg_error='Esta unidad de construcción no existe en la fuente: %d' % buildingunit_src_id, raise_error=True)
            buildingunitchar_src_id = buildingunit_obj[buildingunit_attributes.index('gc_caracteristicasunidadconstruccion')]
            if buildingunitchar_src_id in dict_buildingunitchar:
                buildingunitchar_target_id = dict_buildingunitchar[buildingunitchar_src_id]
            else:
                query = "select "+','.join(buildingunitchar_attributes)+" from \""+schema_src+"\".gc_caracteristicasunidadconstruccion \
                    where id = %d" % buildingunit_obj[buildingunit_attributes.index('gc_caracteristicasunidadconstruccion')]
                buildingunitchar_obj = get_results(conn_src, cursor_src, query, type='one')
                query = "insert into \""+schema_target+"\".gc_caracteristicasunidadconstruccion ("+','.join(buildingunitchar_attributes)+") values \
                    ("+insert_statement(buildingunitchar_obj,buildingunitchar_attributes_types)+") returning id;"
                buildingunitchar_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
                dict_buildingunitchar[buildingunitchar_src_id] = buildingunitchar_target_id
            building_src_id = buildingunit_obj[buildingunit_attributes.index('gc_construccion')]
            if building_src_id in dict_building:
                building_target_id = dict_building[building_src_id]
            else:
                query = "select "+','.join(building_attributes)+" from \""+schema_src+"\".gc_construccion \
                    where id = %d" % building_src_id
                building_obj = get_results(conn_src, cursor_src, query, type='one')
                check_obj(building_obj, msg_error='Esta construcción no existe en la fuente: %d' % building_src_id, raise_error=True)
                query = "insert into \""+schema_target+"\".gc_construccion ("+','.join(building_attributes)+") values \
                    ("+insert_statement(building_obj,building_attributes_types)+") returning id;"
                building_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
                dict_building[building_src_id] = building_target_id
            if buildingunit_src_id in dict_buildingunit:
                buildingunit_target_id = dict_buildingunit[buildingunit_src_id]
            else:    
                buildingunit_obj_ed = list(buildingunit_obj)
                buildingunit_obj_ed[buildingunit_attributes.index('gc_caracteristicasunidadconstruccion')] = buildingunitchar_target_id
                buildingunit_obj_ed[buildingunit_attributes.index('gc_construccion')] = None
                query = "insert into \""+schema_target+"\".gc_unidadconstruccion ("+','.join(buildingunit_attributes)+") values \
                    ("+insert_statement(buildingunit_obj_ed,buildingunit_attributes_types)+") returning id;"
                buildingunit_target_id = get_results(conn_target,cursor_target,query,type='one')[0]
                dict_buildingunit[buildingunit_src_id] = buildingunit_target_id
            col_uebaunit_target_obj_ed = [None for i in range(len(col_uebaunit_attributes))]
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('ue_gc_unidadconstruccion')] = buildingunit_target_id
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('unidad')] = land_target_id
            query = "insert into \""+schema_target+"\".col_uebaunit ("+','.join(col_uebaunit_attributes)+") values \
                ("+insert_statement(col_uebaunit_target_obj_ed,col_uebaunit_attributes_types)+");"
            execute_query(conn_target, cursor_target, query)
        # Migrate transit easement
        query = "select ue_gc_servidumbretransito from \""+schema_src+"\".col_uebaunit where unidad = "+str(land_src_id)+" and ue_gc_servidumbretransito is not null;"
        ue_gc_servidumbretransito_src_ids = get_results(conn_src, cursor_src, query)
        for ue_gc_servidumbretransito_src_id in ue_gc_servidumbretransito_src_ids:
            query = "select "+','.join(transiteasement_attributes)+" from \""+schema_src+"\".gc_servidumbretransito \
                where id = %d" % ue_gc_servidumbretransito_src_id
            transiteasement_obj = get_results(conn_src, cursor_src, query, type='one')
            check_obj(transiteasement_obj, msg_error='Esta servidumbre de transito no existe en la fuente: %d' % ue_gc_servidumbretransito_src_id, raise_error=True)
            query = "insert into \""+schema_target+"\".gc_servidumbretransito ("+','.join(transiteasement_attributes)+") values \
                ("+insert_statement(transiteasement_obj,transiteasement_attributes_types)+") returning id;"
            transiteasement_target_id = get_results(conn_target, cursor_target, query, type='one')[0]
            col_uebaunit_target_obj_ed = [None for i in range(len(col_uebaunit_attributes))]
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('ue_gc_servidumbretransito')] = transiteasement_target_id
            col_uebaunit_target_obj_ed[col_uebaunit_attributes.index('unidad')] = land_target_id
            query = "insert into \""+schema_target+"\".col_uebaunit ("+','.join(col_uebaunit_attributes)+") values \
                ("+insert_statement(col_uebaunit_target_obj_ed,col_uebaunit_attributes_types)+");"
            execute_query(conn_target, cursor_target, query)

    print('Predio migrado %d' % land_src_id)
    return land_target_id