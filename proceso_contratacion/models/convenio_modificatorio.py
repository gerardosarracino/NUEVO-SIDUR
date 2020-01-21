# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo import api, fields, models, _


class ConveniosModificados(models.Model):
    _name = "proceso.convenios_modificado"
    _rec_name = 'contrato'

    # importacion
    id_sideop = fields.Integer()
    num_contrato_sideop = fields.Char()

    # form
    contrato_id = fields.Char(compute="nombre", store=True)
    contrato = fields.Many2one('partidas.partidas', string='Numero Contrato:', readonly=True)

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
    monto_importe = fields.Float(string="Importe:")

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
        print(self.monto_total)

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



