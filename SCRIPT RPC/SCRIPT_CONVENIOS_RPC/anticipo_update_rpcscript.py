import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

numero_contrato_id = odoo.env['partidas.partidas'].search([]) # ("nombre_partida", "=", 'SIDUR-ED-19-207.1866')

# obra = odoo.env['registro.programarobra'].search([])

for x in numero_contrato_id:
    print(' START')
    b_partida = odoo.env['partidas.partidas'].browse(x)
    for i in b_partida:
        monto_original = i.monto_partida

        anticipo_a = monto_original * i.total_anticipo_porcentaje

        iva_anticipo = anticipo_a * i.b_iva

        total_anticipo = anticipo_a + iva_anticipo

        b_partida.write({'anticipo_a': anticipo_a, 'iva_anticipo': iva_anticipo, 'total_anticipo': total_anticipo})
        print('EXITO!!!!', i.nombre_partida)