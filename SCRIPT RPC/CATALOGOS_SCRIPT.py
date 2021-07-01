import odoorpc

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('localhost', port=1269)
odoo.login('sidur2021', usuario, password)

_search_partida = odoo.env['partidas.partidas'].search([("id", "=", '1')])
concepto = odoo.env['proceso.conceptos_part'].search([("id_partida.id", "=", '1')])
print(_search_partida, '--')
print(concepto)
b_partx = odoo.env['partidas.partidas'].browse(_search_partida)
b_c = odoo.env['proceso.conceptos_part'].browse(concepto)

for i in b_partx:
    for c in b_c:
        datos_esti = {
            'conceptos_partidas': [[4, c.id, {
            }]]}
        partida_nueva = i.write(datos_esti)
