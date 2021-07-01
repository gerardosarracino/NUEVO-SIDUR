import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

try:
    # partidas = odoo.env['partidas.partidas'].search([('ejercicio', '=', '2019')]) # ,('idobra', '=', '19')
    partidas = odoo.env['partidas.partidas'].search([('nombre_partida', '=', 'SIDUR-ED-19-138.1788')]) # ,('idobra', '=', '19')
    for x in partidas:
        print(' START')
        b_estimaciones = odoo.env['partidas.partidas'].browse(x)
        for b in b_estimaciones.conceptos_partidas:
            print(' INICIA CICLO')
            # CASO CATEGORIA
            if b.clave_linea and b.concepto and not b.precio_unitario and not b.categoria.parent_id.id and not b.related_categoria_padre:
                print(' CATEGORIA SIN GRUPO')
                b.write({'related_categoria_padre': b.categoria.id})
            elif b.clave_linea and b.concepto and not b.precio_unitario and b.categoria.parent_id.id and not b.related_categoria_padre.id:
                print(' CON CATEGORIA PERO SIN GRUPO')
                b.write({'related_categoria_padre': b.categoria.parent_id.id})
                # b.write({'related_categoria_padre': nombre_categoria, 'categoria': categoria_relatedx2})
            # CASO CONCEPTO
            elif b.precio_unitario:
                # if not b.related_categoria_padre.parent_id.id:
                if b.related_categoria_padre.parent_id and not b.categoria:
                    print(' CONCEPTO SIN CATEGORIA PERO CON SUBGRUPO')
                    b.write({'categoria': b.related_categoria_padre.id})

                elif not b.related_categoria_padre.parent_id and b.related_categoria_padre and not b.categoria:
                    print(' CONCEPTO SIN CATEGORIA PERO CON GRUPO')
                    nombre_categoriax2 = b.related_categoria_padre.id
                    b.write({'categoria': nombre_categoriax2})
            else:
                print(' nada')
except:
    print('ERERO')


