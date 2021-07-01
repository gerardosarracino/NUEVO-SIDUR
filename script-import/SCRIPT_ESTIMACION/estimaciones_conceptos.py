import odoorpc, csv
import datetime
import mysql.connector

import time

usuario = 'admin'
password = 'Sp1d3rb0r4s2020'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='sidur.galartec.com',
                              database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `estimaciones_detalles` INNER JOIN catalogoconceptos ON estimaciones_detalles.id_concepto = catalogoconceptos.id where num_contrato = 'SIDUR-PF-17-227.987' and num_estimacion = '17' order by catalogoconceptos.id asc")
# where catalogoconceptos.id > "+str(ultimo_row_OK)+" where estimaciones_detalles.id_concepto > 148383  and num_estimacion = '5'

cursor.execute(query)

for row in cursor:
    contrato = odoo.env['partidas.partidas']

    print(row['num_contrato'], ' y la id es x', row['id'], ' numero estimacion es x', row['num_estimacion'])

    '''_search_estimacion = odoo.env['control.estimaciones'].search_count(
        [("obra", "=", row['num_contrato']), ("idobra", "=", row['num_estimacion'])])

    if _search_estimacion == 0:
        print('NO EXISTE ESTA ESTIMACION', row['num_contrato'])
    else:'''
    # print('EXISTE ESTIMACION')

    _search_estimacion2 = odoo.env['control.estimaciones'].search(
        [("obra", "=", row['num_contrato']), ("idobra", "=", row['num_estimacion']),
         ("tipo_estimacion", "=", '1')])

    _search_estimacion3 = odoo.env['control.estimaciones'].browse(_search_estimacion2)



    _search_detalle = odoo.env['control.detalle_conceptos'].search(
        [("id_partida", "=", _search_estimacion3.obra.id), ("num_est", "=", row['num_estimacion']),
         ("clave_linea", "=",  str(row['clave']))])

    if _search_detalle:
        pass
    else:

        # _search_partida = odoo.env['partidas.partidas'].search([("id_contrato_sideop", "=", row['num_contrato'])])
        _search_categoria = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                  limit=1)
        categorias = odoo.env['catalogo.categoria']

        if str(_search_categoria) is not '[]':
            categoria = _search_categoria
            _search_cat = odoo.env['catalogo.categoria'].search(
                [("id_sideop", "=", row['idpadre'])])
            categoria = categorias.browse(_search_cat)
            categoria = categoria.id
        else:
            categoria = None

        categoriasx = odoo.env['catalogo.categoria']

        _search_parent_id = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                  )
        b_parent = categoriasx.browse(_search_parent_id)

        '''if str(row['cantidad_ejecutada_current']) == '96..6':
            ctdec = '41.86'
        else:
            ctdec = str(row['cantidad_ejecutada_current'])'''

        print('yeeesss', _search_detalle, str(row['clave']))

        print(row['num_estimacion'], str(row['clave']), '---')
        datos_conceptos = {
            'conceptos_partidas': [[0, 0, {
                'num_est': row['num_estimacion'],
                'numero_estimacion_group': 'Estimación ' + str(row['num_estimacion']),
                'id_partida': _search_estimacion3.obra.id,
                'related_categoria_padre': b_parent.id,
                'categoria': categoria,
                'clave_linea': str(row['clave']),
                'concepto': str(row['descripcion']),
                'medida': str(row['unidad']),
                'precio_unitario': str(row['punitario']),
                'cantidad': str(row['cantidad']),
                'importe_ejecutado': float(row['punitario']) * float(row['cantidad_ejecutada_current']),
                # 'id_detalle': str(row['id']),
                'estimacion': str(row['cantidad_ejecutada_current']),
            }]]}

        partida_nueva = _search_estimacion3.write(datos_conceptos)
        print(' EXIIIITOOOOOOOO!!!!!')


                
    
   
