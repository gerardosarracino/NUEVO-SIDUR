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
doc = DocxTemplate("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/INV_LIC_PUBLICA_DGPI/12_LPO-XXX_DGPI.DOCX")  # nuevo
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
        visita = x.visitafechahora.strftime("%A")
        if visita == 'Monday':
            visita = nombre_dias[1]
        elif visita == 'Tuesday':
            visita = nombre_dias[2]
        elif visita == 'Wednesday':
            visita = nombre_dias[3]
        elif visita == 'Thursday':
            visita = nombre_dias[4]
        elif visita == 'Friday':
            visita = nombre_dias[5]
        elif visita == 'Saturday':
            visita = nombre_dias[6]
        elif visita == 'Sunday':
            visita = nombre_dias[7]
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

        fecha = str(nd) + " " + str(ahora.day) + " de " + meses[ahora.month] + " del " + str(ahora.year)

        fecha_junta = str(junta) + " " + str(x.juntafechahora.day) + " de " + meses[x.juntafechahora.month] + " del " + \
                      str(x.juntafechahora.year) + ' a las ' + str(x.juntafechahora.hour) + ':' + str(x.juntafechahora.minute) + '0 Horas'

        fecha_visita = str(visita) + " " + str(x.visitafechahora.day) + " de " + meses[x.visitafechahora.month] \
                       + " del " + str(x.visitafechahora.year) \
                      + ' a las ' + str(x.visitafechahora.hour) + ':' + str(x.visitafechahora.minute) + '0 Horas'

        dia = ahora.day
        mes = ahora.month
        year = ahora.year
        context = {
            'fecha_completa': fecha,
            'fecha_visita': fecha_visita,
            'fecha_junta': fecha_junta,
            'dia': dia,
            'mes': mes,
            'year': year,
            'numero_licitacion': numero_licitacion,
            'concepto': x.name,
            'lugar_visita': x.visitalugar,
        }
        doc.render(context)
        doc.save("generated_doc.docx")

