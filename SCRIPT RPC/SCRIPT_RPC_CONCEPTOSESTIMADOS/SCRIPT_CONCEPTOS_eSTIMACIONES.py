import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'Sp1d3rb0r4s2020'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

partidas = odoo.env['control.detalle_conceptos'].search([('id_partida', '=', 'SIDUR-PF-17-227.987'),('num_est', '=', 42), ('id', '>', 306675)]) # ,('idobra', '=', '4')
for x in partidas:
    print(' START')
    b_estimaciones = odoo.env['control.detalle_conceptos'].browse(x)

    for b in b_estimaciones:
        print('-----------------------', b.clave_linea, b.related_categoria_padre.id, b.id) # 47277
        b.write({'categoria': 47277, 'related_categoria_padre': 47277})
        '''print(' INICIA CICLO')
        # CASO CATEGORIA
        if b.clave_linea and b.concepto and not b.precio_unitario and not b.categoria.parent_id.id and not b.related_categoria_padre:
            print(' CATEGORIA SIN GRUPO')
            b.write({'related_categoria_padre': b.categoria.id})

        elif b.clave_linea and b.concepto and not b.precio_unitario and b.categoria.parent_id.id and not b.related_categoria_padre.id:
            print(' CON CATEGORIA PERO SIN GRUPO')
            b.write({'related_categoria_padre': b.categoria.parent_id.id})
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
            print(' nada')'''

