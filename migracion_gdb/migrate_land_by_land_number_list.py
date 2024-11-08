import psycopg2
from helpers.migrate_land_limited import migrate_land_limited

#Params conection src
src_host = 'localhost'
src_database = 'V1_municipios_1dic2023'
src_user = 'postgres'
src_password = 'prod8cci0n2021'
src_port = '5432'

#Params conection target
target_host = 'localhost'
target_database = 'V1_municipios'
target_user = 'postgres'
target_password = 'prod8cci0n2021'
target_port = '5432'

withGeom = True

land_number_list = [
'250350002000000150901900000692',
'250350002000000150901900000693',
'250350002000000150901900000694',
'250350002000000150901900000695',
'250350002000000150901900000696',
'250350002000000150901900000697',
'250350002000000150901900000698',
'250350002000000150901900000699',
'250350002000000150901900000700',
'250350002000000150901900000701',
'250350002000000150901900000702',
'250350002000000150901900000703',
'250350002000000150901900000704',
'250350002000000150901900000705',
'250350002000000150901900000706',
'250350002000000150901900000707',
'250350002000000150901900000708',
'250350002000000150901900000709',
'250350002000000150901900000710',
'250350002000000150901900000711',
'250350002000000150901900000712',
'250350002000000150901900000713',
'250350002000000150901900000714',
'250350002000000150901900000715',
'250350002000000150901900000716',
'250350002000000150901900000717',
'250350002000000150901900000718',
'250350002000000150901900000719',
'250350002000000150901900000720',
'250350002000000150901900000721',
'250350002000000150901900000722',
'250350002000000150901900000723',
'250350002000000150901900000724',
'250350002000000150901900000725',
'250350002000000150901900000726',
'250350002000000150901900000727',
'250350002000000150901900000728',
'250350002000000150901900000729'
]

#-----------------------
# Code
#-----------------------

#Conection BD ladm old
conn_target = psycopg2.connect(
    host= target_host,
    database= target_database,
    user= target_user,
    password= target_password,
    port= target_port)
cursor_target = conn_target.cursor()

#Conection BD ladm new
conn_src = psycopg2.connect(
    host= src_host,
    database= src_database,
    user= src_user,
    password= src_password,
    port= src_port)
cursor_src = conn_src.cursor()

def execute_query(conn, cursor, query):
    cursor.execute(query)
    conn.commit()

def get_results(conn, cursor, query, type='all'):
    execute_query(conn, cursor, query)
    if type == 'one':
        return cursor.fetchone()
    else:
        return cursor.fetchall()

#main
for land_number in land_number_list:
    schema = 'cun%s' % land_number[0:5]
    query = "select id from \""+schema+"\".gc_predio where numero_predial='%s'" % land_number
    land_id = get_results(conn_src, cursor_src, query, type='one')[0]
    check_land_id_list = get_results(conn_target, cursor_target, query)
    if len(check_land_id_list) != 0:
        print("Este predio ya existe en la base de datos de destino: %s" % land_number)
        continue
    dict_parties = {}
    migrate_land_limited(conn_src,cursor_src,conn_target,cursor_target, schema, schema, land_id, dict_parties, withGeom)