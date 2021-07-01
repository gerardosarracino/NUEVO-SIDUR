import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'Sp1d3rb0r4s2020'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

imagenes = odoo.env['semaforo.fotos_i'].search([])


for x in imagenes:
    print(' START')
    b_imagen = odoo.env['semaforo.fotos_i'].browse(x)
    for b in b_imagen:
        print(b.image_medium)
        '''image = b.fotos
        data = tools.image_get_resized_images(image)
        image_medium = data["image_medium"]'''

        # b.write({'image_medium': image_medium,})
        print('EXITO', )

