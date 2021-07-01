import odoorpc

from datetime import datetime
from docxtpl import DocxTemplate
# from jinja2 import Template
# import json
import time
import binascii #nuevo
from num2words import num2words

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

licitacion = odoo.env['proceso.licitacion'].search([('numerolicitacion', '=', 'LPO-926006995-013-2020')])
doc = DocxTemplate("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/13_LP_XXX_BASES/13_LPO-XXX_BASES.DOCX")  # nuevo
for i in licitacion:
    b_lic = odoo.env['proceso.licitacion'].browse(i)
    for x in b_lic:

        for rec in x.programar_obra_licitacion:
            oficio = rec.recursos.name.name
            fecha_oficio_ = rec.recursos.name.fecha_actual

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

        fecha_visita = str(visita) + " " + str(x.visitafechahora.day) + " de " + meses[x.visitafechahora.month] \
                       + " del " + str(x.visitafechahora.year)
        visita_hora = str(x.visitafechahora.hour) + ':' + str(x.visitafechahora.minute) + '0 Horas'

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

        fecha_apertura = str(apertura) + " " + str(x.aperturafechahora.day) + " de " + meses[x.aperturafechahora.month] \
                       + " del " + str(x.aperturafechahora.year)
        apertura_hora = str(x.aperturafechahora.hour) + ':' + str(x.aperturafechahora.minute) + '0 Horas'

        fallo = x.fallofechahora.strftime("%A")
        if fallo == 'Monday':
            fallo = nombre_dias[1]
        elif fallo == 'Tuesday':
            fallo = nombre_dias[2]
        elif fallo == 'Wednesday':
            fallo = nombre_dias[3]
        elif fallo == 'Thursday':
            fallo = nombre_dias[4]
        elif fallo == 'Friday':
            fallo = nombre_dias[5]
        elif fallo == 'Saturday':
            fallo = nombre_dias[6]
        elif fallo == 'Sunday':
            fallo = nombre_dias[7]

        fecha_fallo = str(fallo) + " " + str(x.fallofechahora.day) + " de " + meses[x.fallofechahora.month] \
                         + " del " + str(x.fallofechahora.year)
        fallo_hora = str(x.fallofechahora.hour) + ':' + str(x.fallofechahora.minute) + '0 Horas'

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

        fecha_junta = str(junta) + " " + str(x.juntafechahora.day) + " de " + meses[x.juntafechahora.month] + " del " + \
                      str(x.juntafechahora.year)
        hora_junta = str(x.juntafechahora.hour) + ':' + str(x.juntafechahora.minute) + '0 Horas'

        fecha = str(nd) + " " + str(ahora.day) + " de " + meses[ahora.month] + " del " + str(ahora.year)

        fecha_con_inv = str(x.fechaconinv.day) + " de " + meses[x.fechaconinv.month] + " del " + str(x.fechaconinv.year)

        fecha_oficio = str(fecha_oficio_.day) + " de " + meses[fecha_oficio_.month] + " del " + str(fecha_oficio_.year)

        fecha_inicio_licitacion = str(x.fechaestimadainicio.day) + " de " + meses[x.fechaestimadainicio.month] + " del " + str(x.fechaestimadainicio.year)
        fecha_termino_licitacion = str(x.fechaestimadatermino.day) + " de " + meses[x.fechaestimadatermino.month] + " del " + str(x.fechaestimadatermino.year)
        fecha_limite_bases = str(x.fechalimiteentregabases.day) + " de " + meses[x.fechalimiteentregabases.month] \
                             + " del " + str(x.fechalimiteentregabases.year)

        dia = ahora.day
        mes = ahora.month
        mes_letra = meses[fechaconinv.month]
        year = fechaconinv.year
        context = {
            'fecha_completa': fecha,
            'fecha_con_inv': fecha_con_inv,
            'fecha_limite_bases': fecha_limite_bases,
            'dia': dia,
            'mes_letra': mes_letra,
            'year': year,
            'numero_licitacion': numero_licitacion,
            'concepto': x.name,
            'oficio': oficio,
            'fecha_oficio': fecha_oficio,
            'plazo_dias': x.plazodias,
            'fecha_inicio_licitacion': fecha_inicio_licitacion,
            'fecha_termino_licitacion': fecha_termino_licitacion,
            'fecha_visita': fecha_visita,
            'visita_hora': visita_hora,
            'lugar_visita': x.visitalugar,
            'fecha_junta': fecha_junta,
            'hora_junta': hora_junta,
            'lugar_junta': x.juntalugar,
            'fecha_apertura': fecha_apertura,
            'apertura_hora': apertura_hora,
            'lugar_apertura': x.aperturalugar,
            'fecha_fallo': fecha_fallo,
            'fallo_hora': fallo_hora,
            'lugar_fallo': x.fallolugar,
            'capital_contable': '{:20,.2f}'.format(x.capitalcontable),
            'capital_contable_letra': num2words(x.capitalcontable, lang='es'),
            'anticipo_inicio': int(x.anticipoinicio),
            'porcentaje_letra': num2words(x.anticipoinicio, lang='es'),
        }
        doc.render(context)
        doc.save("generated_doc.docx")

