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
doc = DocxTemplate("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/invitacion_licitacion_publica/Invitación_Licitación_Pública.DOCX")  # nuevo
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
        nd = ahora.strftime("%A")
        if nd == 'Monday':
            nd = nombre_dias[1]
        elif nd == 'Tuesday':
            nd = nombre_dias[2]
        elif nd == 'Wednesday':
            nd = nombre_dias[3]
        elif nd == 'Thursday':
            nd = nombre_dias[4]
        elif nd == 'Friday':
            nd = nombre_dias[5]
        elif nd == 'Saturday':
            nd = nombre_dias[6]
        elif nd == 'Sunday':
            nd = nombre_dias[7]
        apertura = x.aperturafechahora.strftime("%A")
        if apertura == 'Monday':
            apertura = nombre_dias[1]
        elif apertura == 'Tuesday':
            apertura = nombre_dias[2]
        elif apertura == 'Wednesday':
            apertura = nombre_dias[3]
        elif apertura == 'Thursday':
            apertura = nombre_dias[4]
        elif apertura == 'Friday':
            apertura = nombre_dias[5]
        elif apertura == 'Saturday':
            apertura = nombre_dias[6]
        elif apertura == 'Sunday':
            apertura = nombre_dias[7]

        junta = x.juntafechahora.strftime("%A")
        if junta == 'Monday':
            junta = nombre_dias[1]
        elif junta == 'Tuesday':
            junta = nombre_dias[2]
        elif junta == 'Wednesday':
            junta = nombre_dias[3]
        elif junta == 'Thursday':
            junta = nombre_dias[4]
        elif junta == 'Friday':
            junta = nombre_dias[5]
        elif junta == 'Saturday':
            junta = nombre_dias[6]
        elif junta == 'Sunday':
            junta = nombre_dias[7]

        fecha = str(ahora.day) + " de " + meses[ahora.month] + " del " + str(ahora.year)

        fecha_junta = str(x.juntafechahora.day) + " de " + meses[x.juntafechahora.month] + " del " + \
                      str(x.juntafechahora.year) + ' a las ' + str(x.juntafechahora.hour) + ':' + str(x.juntafechahora.minute) + '0 Horas'

        fecha_apertura = str(x.aperturafechahora.day) + " de " + meses[x.aperturafechahora.month] \
                       + " del " + str(x.aperturafechahora.year) \
                      + ' a las ' + str(x.visitafechahora.hour) + ':' + str(x.visitafechahora.minute) + '0 Horas'

        dia = ahora.day
        mes = ahora.month
        year = ahora.year
        context = {
            'fecha_completa': fecha,
            'fecha_junta': fecha_junta,
            'fecha_apertura': fecha_apertura,
            'numero_licitacion': numero_licitacion,
            'concepto': x.name,
        }
        doc.render(context)
        doc.save("generated_doc.docx")

