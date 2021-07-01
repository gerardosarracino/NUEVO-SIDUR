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

# try:
# busca_platilla = http.request.env['plantillas.plantillas'].sudo().browse(int(id))[0]  # nuevo
# xd = binascii.a2b_base64(licitacion.subir_documento)  # nuevo

doc = DocxTemplate("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/PRUEBA/doc2.docx")  # nuevo

'''with open("/home/gerardo/Escritorio/SCRIPT RPC/DOCUMENTOS SCRIPT/PRUEBA/doc2.doc", 'wb') as file:  # nuevo
    file.write(xd)  # nuevo'''

# finiquito = http.request.env['partidas.partidas'].sudo().browse(int(contrato))[0]

for i in licitacion:
    b_lic = odoo.env['proceso.licitacion'].browse(i)

    for x in b_lic:

        numero_licitacion = x.numerolicitacion
        # fecha_termino_trabajos = f.fecha1.strftime("%d/%m/%Y")

        context = {
            'numero_licitacion': numero_licitacion,
        }

        doc.render(context)
        doc.save("generated_doc.docx")
    # contratistas = http.request.env['contratista.contratista'].sudo().browse(int(contratista))[0]

    '''for c in contratistas:
        contratista = c.name'''

    '''obras = http.request.env['registro.programarobra'].sudo().browse(int(obra))[0]
    for o in obras:
        descripcion_obra = o.descripcion'''

    '''ahora = datetime.now()
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

    fecha = str(nd) + " " + str(ahora.day) + " de " + meses[ahora.month] + " de " + str(ahora.year)
    dia = ahora.day
    mes = ahora.month
    year = ahora.year'''



'''except Exception as e:
    return "Upss! algo salio mal. Error en: " + str(e)'''


