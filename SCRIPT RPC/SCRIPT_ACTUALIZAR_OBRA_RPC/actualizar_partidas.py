import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'Sp1d3rb0r4s2020'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

numero_contrato_id = odoo.env['partidas.partidas'].search([("nombre_partida", "=", 'SIDUR-ED-20-010.2009')]) # ("nombre_partida", "=", 'SIDUR-ED-19-133.1779')

# obra = odoo.env['registro.programarobra'].search([])

for x in numero_contrato_id:
    print(' START')
    b_partida = odoo.env['partidas.partidas'].browse(x)
    for b in b_partida:
        datos = {'ejercicio': b.numero_contrato.ejercicio.id}
        xx = b_partida.write(datos)
        print('exito xd')

