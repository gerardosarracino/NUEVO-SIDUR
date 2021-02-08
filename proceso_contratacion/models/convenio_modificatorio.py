# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo import api, fields, models, _


class ConveniosModificados(models.Model):
    _name = "proceso.convenios_modificado"
    _rec_name = 'contrato_contrato'

    # importacion
    id_sideop = fields.Integer()
    num_contrato_sideop = fields.Char()

    # form
    contrato_id = fields.Char(compute="nombre", store=True)
    contrato = fields.Many2one('partidas.partidas', string='Numero Partida:')
    contrato_contrato = fields.Many2one('proceso.elaboracion_contrato', string='Numero Contrato:')
    nombre_contrato = fields.Char(string='Nombre Contrato:') # para metodo

    fecha_convenios = fields.Date(string="Fecha:")
    name_convenios = fields.Many2one('registro.programarobra', string="obra partida", related="contrato.obra")
    referencia = fields.Char(string="Referencia:")
    observaciones = fields.Text(string="Observaciones:")
    fecha_dictamen = fields.Date(string="Fecha Dictamen:")

    # RADIO BUTTON
    radio = [(
        'PL', "Plazo"), ('OB', "Objeto"), ('MT', "Monto"), ('BOTH', "Monto/Plazo"), ]
    tipo_convenio = fields.Selection(radio, string="Tipo de Convenio:")

    # CONDICION PLAZO
    plazo_fecha_inicio = fields.Date(string="Fecha Inicio:")
    plazo_fecha_termino = fields.Date(string="Fecha Termino:")
    # CONDICION OBJETO
    objeto_nuevo_objeto = fields.Text(string="Objeto:")
    # CONDICION MONTO
    select_monto = [(
        'AM', "Ampliación:"), ('RE', "Reducción:")]
    tipo_monto = fields.Selection(select_monto, string="Monto:")
    monto_importe = fields.Float(string="Importe:", store=True)

    monto_iva = fields.Float(string="I.V.A:", compute="iva_calc")

    monto_total = fields.Float(string="Total:", compute="sumaMonto")
    # CONDICION MONTO PLAZO
    # TERMINA CONDICIONES RADIO BUTTON

    convenio_fecha_fianza = fields.Date(string="Fecha Fianza:")
    convenio_numero_fianza = fields.Char(string="Numero Fianza:")
    convenio_afianzadora = fields.Char(string="Afianzadora:")
    convenio_monto_afianzadora = fields.Float(string="Monto Fianza:")

    estatus_convenio = fields.Selection(
        [('borrador', 'Contratista sin Anticipo'), ('confirmado', 'Contratista con Anticipo'), ('validado', 'Convenio Validado'), ],
        default='borrador')

    @api.model
    def create(self, values):
        _search_cove = self.env['proceso.convenios_modificado'].search([("contrato", "=", values['contrato'])])
        _search_part = self.env['partidas.partidas'].search([("nombre_contrato", "=", str(values['nombre_contrato']))])
        print(_search_part, ' xxdfasd')
        acum = 0
        acum2 = 0
        total = 0
        for vals in _search_cove:
            if vals['tipo_monto'] == 'AM':
                acum = acum + vals['monto_importe']
            elif vals['tipo_monto'] == 'RE':
                acum2 = acum2 + vals['monto_importe']
            ampliacion = acum
            reduccion = acum2
            total = ampliacion - reduccion
        totalx = total + values['monto_importe']
        if values['tipo_convenio'] == 'MT':
            for i in _search_part:
                b_contrato = self.env['partidas.partidas'].browse(i['id'])
                print(b_contrato, ' alv')
                total_civa = ((b_contrato['monto_partida'] + totalx) * b_contrato['b_iva']) + (b_contrato['monto_partida'] + totalx)
                b_contrato.write({'total': totalx + b_contrato['monto_partida'], 'total_civa': total_civa})
                print(b_contrato.write({'total': totalx + b_contrato['monto_partida'], 'total_civa': total_civa}))
        elif values['tipo_convenio'] == 'BOTH':
            for i in _search_part:
                b_contrato = self.env['partidas.partidas'].browse(i['id'])
                total_civa = ((b_contrato['monto_partida'] + totalx) * b_contrato['b_iva']) + (
                            b_contrato['monto_partida'] + totalx)
                b_contrato.write({'total': totalx + b_contrato['monto_partida'], 'total_civa': total_civa,
                                  'fecha_inicio_convenida': values['plazo_fecha_inicio'],
                                  'fecha_termino_convenida': values['plazo_fecha_termino']})
        elif values['tipo_convenio'] == 'PL':
            for i in _search_part:
                b_contrato = self.env['partidas.partidas'].browse(i['id'])
                b_contrato.write({'fecha_inicio_convenida': values['plazo_fecha_inicio'], 'fecha_termino_convenida': values['plazo_fecha_termino']})
        else:
            pass
        return super(ConveniosModificados, self).create(values)

    '''@api.multi
    def write(self, values):
        contadorx = self.env['proceso.convenios_modificado'].search_count([("nombre_contrato", "=", self.nombre_contrato)])
        _search_cove = self.env['proceso.convenios_modificado'].search([("nombre_contrato", "=", self.nombre_contrato)])
        _search_partida = self.env['partidas.partidas'].search([("nombre_contrato", "=", self.nombre_contrato)])

        for i in _search_partida:
            b_part = self.env['partidas.partidas'].browse(i.id)
            for b_contrato in b_part:
                acum = 0
                acum2 = 0
                contador = 0
                total = 0
                id_c = ''
                for y in _search_cove:
                    contador += 1
                    if y.tipo_monto == 'AM':
                        acum = acum + y.monto_importe
                    elif y.tipo_monto == 'RE':
                        acum2 = acum2 + y.monto_importe
                    ampliacion = acum
                    reduccion = acum2
                    total = ampliacion - reduccion
                    id_c = y.id

                if self.id == id_c:
                    if self.tipo_convenio == 'MT':
                        total_civa = ((b_contrato.monto_partida + total) * b_contrato.b_iva) + (b_contrato.monto_partida + total)

                        b_part.write({'total': total + b_contrato.monto_partida, 'total_civa': total_civa})
                    elif self.tipo_convenio == 'BOTH':
                        total_civa = ((b_contrato.monto_partida + total) * b_contrato.b_iva) + (b_contrato.monto_partida + total)

                        b_part.write({'total': total + b_contrato.monto_partida, 'total_civa': total_civa,
                                         'fecha_inicio_convenida': str(self.plazo_fecha_inicio),
                                         'fecha_termino_convenida': str(self.plazo_fecha_termino)})
                    elif self.tipo_convenio == 'PL':
                        b_part.write({'fecha_inicio_convenida': str(self.plazo_fecha_inicio),
                                         'fecha_termino_convenida': str(self.plazo_fecha_termino)})
                    else:
                        pass
                else:
                    pass'''

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_convenio': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_convenio': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_convenio': 'validado'})

    @api.one
    def nombre(self):
        self.contrato_id = self.id

    @api.one
    @api.depends('monto_importe', 'monto_iva')
    def sumaMonto(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.monto_total = (self.monto_importe * float(iva)) + self.monto_importe

    @api.one
    @api.depends('monto_total')
    def iva_calc(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.monto_iva = (self.monto_importe * float(iva))

    @api.one
    @api.depends('monto_plazo_importe', 'monto_plazo_iva')
    def sumaMontoPlazo(self):
        for rec in self:
            rec.update({
                'monto_plazo_total': (rec.monto_plazo_importe * rec.monto_plazo_iva) + rec.monto_plazo_importe
            })



