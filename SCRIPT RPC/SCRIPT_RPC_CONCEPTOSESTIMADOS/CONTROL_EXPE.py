import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

try:
    partidas = odoo.env['partidas.partidas'].search([('ejercicio', '=', '2015')]) # ,('idobra', '=', '19')
    for x in partidas:
        print(' START')
        b_estimaciones = odoo.env['partidas.partidas'].browse(x)

        for b in b_estimaciones.tabla_control:
            b.write({'responsable': b.nombre.responsable.id})
            print('EXITO', b_estimaciones.nombre_partida)
except:
    print('ERERO')


