import odoorpc

from datetime import datetime
from docxtpl import DocxTemplate
# from jinja2 import Template
# import json
import time
import binascii #nuevo

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

licitacion = odoo.env['proceso.licitacion'].search([('numerolicitacion', '=', 'LPO-926006995-013-2020')])
doc = DocxTemplate("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/publicacion_convocatoria_lpo_sol_pub_bof/04_LPO-XXX_SOL_PUB_BOF.DOCX")  # nuevo
for i in licitacion:
    b_lic = odoo.env['proceso.licitacion'].browse(i)
    for x in b_lic:
        numero_licitacion = x.numerolicitacion
        ahora = datetime.now()
        meses = ["Unknown",
                 "Enero",
                 "Febrero",
                 "Marzo",
                 "Abril",
                 "Mayo",
                 "Junio",
                 "Julio",
                 "Agosto",
                 "Septiembre",
                 "Octubre",
                 "Noviembre",
                 "Diciembre"]
        nombre_dias = [
            "Unknown",
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo"]

        dia_fecha_con_inv = x.fechaconinv.strftime("%A")
        if dia_fecha_con_inv == 'Monday':
            dia_fecha_con_inv = nombre_dias[1]
        elif dia_fecha_con_inv == 'Tuesday':
            dia_fecha_con_inv = nombre_dias[2]
        elif dia_fecha_con_inv == 'Wednesday':
            dia_fecha_con_inv = nombre_dias[3]
        elif dia_fecha_con_inv == 'Thursday':
            dia_fecha_con_inv = nombre_dias[4]
        elif dia_fecha_con_inv == 'Friday':
            dia_fecha_con_inv = nombre_dias[5]
        elif dia_fecha_con_inv == 'Saturday':
            dia_fecha_con_inv = nombre_dias[6]
        elif dia_fecha_con_inv == 'Sunday':
            dia_fecha_con_inv = nombre_dias[7]

        fecha = str(ahora.day) + " de " + meses[ahora.month] + " del " + str(ahora.year)

        fecha_con_inv = str(x.fechaconinv.day) + " de " + meses[x.fechaconinv.month] + " del " + \
                      str(x.fechaconinv.year)

        fecha_oficio = str(x.fechaoficio2.day) + " de " + meses[x.fechaoficio2.month] + " del " + str(
            x.fechaoficio2.year)

        context = {
            'fecha_oficio': fecha_oficio,
            'dia_fecha_con_inv': dia_fecha_con_inv,
            'fecha_con_inv': fecha_con_inv,
            'numero_licitacion': numero_licitacion,
            'concepto': x.name,
            'convocatoria': x.convocatoria,
        }
        doc.render(context)
        doc.save("generated_doc.docx")

