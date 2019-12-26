# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
from docxtpl import DocxTemplate
from jinja2 import Template




class ProcesoContratacion(http.Controller):
    @http.route('/documento/<contrato>', type='http', auth='public', website=True)
    def contrato(self, contrato):
        try:

            doc = DocxTemplate(
                "/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/proceso_contratacion/templates/PERSONA_FISICA_CONTRATO.docx")

            qwerty = http.request.env['proceso.elaboracion_contrato'].sudo().browse(int(contrato))[0]
            for i in qwerty:
                adjudicacion = i.adjudicacion
                contrato = i.contrato  # Número de contrato
                fecha = i.fecha.strftime("%d/%m/%Y")  # Fecha actual
                descripcion_meta = i.name
                descripcion_trabajos = i.descripciontrabajos
                supervicion_externa = i.supervisionexterna
                fecha_inicio = i.fechainicio.strftime("%d/%m/%Y")
                fecha_termino = i.fechatermino.strftime("%d/%m/%Y")
                adjudicacion = i.adjudicacion.numerocontrato
                contratista = i.contratista.name
                periodo_retencion = i.periodicidadretencion
                unidad_resposable = i.unidadresponsableejecucion.name
                retencion = i.retencion

            obra_partida_descripcion = ""
            for o in qwerty.contrato_partida_adjudicacion:
                obra_partida_descripcion = obra_partida_descripcion + " " + o.obra.descripcion
                monto_partida = o.monto_partida
                iva_partida = o.iva_partida
                total_partida = o.total_partida

            partidas = http.request.env['partidas.partidas'].sudo().browse(int(o))[0]
            for pp in partidas.programaInversion:
                programa_inversion = pp.name

            context = {
                'adjudicacion': adjudicacion,
                'contrato': contrato,
                'fecha': fecha,
                'descripcion_meta': descripcion_meta,
                'descripcion_trabajos': descripcion_trabajos,
                'supervicion_externa': supervicion_externa,
                'fecha_inicio': fecha_inicio,
                'fecha_termino': fecha_termino,
                'programa_inversion': programa_inversion,
                'partidas': obra_partida_descripcion,
                'monto_partida': monto_partida,
                'iva_partida': iva_partida,
                'total_partida': total_partida,
                'contratista': contratista,
                'periodo_retencion': periodo_retencion,
                'unidad_resposable': unidad_resposable,
                'retencion': retencion

            }

            doc.render(context)
            doc.save("/tmp/generated_doc.docx")
            nombre = "doc.docx"
            f = open('/tmp/generated_doc.docx', mode="rb")
            return http.request.make_response(f.read(),
                                              [('Content-Type', 'application/octet-stream'),
                                               ('Content-Disposition',
                                                'attachment; filename="{}"'.format(nombre))
                                               ])
        except:
            return "Upss! algo salio mal"


class Test_(http.Controller):
    @http.route('/test',  type='http', auth='public', website=True)
    def test(self):
           
        doc = DocxTemplate("/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/proceso_contratacion/templates/PERSONA_FISICA_CONTRATO.docx")
        
        
        context = { 'company_name' : "World company" }
        
        doc.render(context)
        
        doc.save("/tmp/generated_doc.docx")
        nombre = "doc.docx"
        f = open('/tmp/generated_doc.docx', mode="rb")
        return http.request.make_response(f.read(),
                                            [('Content-Type', 'application/octet-stream'),
                                            ('Content-Disposition',
                                                'attachment; filename="{}"'.format(nombre))
                                            ])