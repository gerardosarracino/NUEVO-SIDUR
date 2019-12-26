# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo import api, fields, models, _


class ConveniosModificados(models.Model):
    _name = "proceso.convenios_modificado"
    _rec_name = 'contrato'

    contrato_id = fields.Char(compute="nombre", store=True)

    contrato = fields.Many2one('partidas.partidas', string='Numero Contrato:', readonly=True)

    fecha_convenios = fields.Date(string="Fecha:")
    name_convenios = fields.Many2one('registro.programarobra', string="obra partida", related="contrato.obra")
    referencia = fields.Char(string="Referencia:")
    observaciones = fields.Text(string="Observaciones:")
    fecha_dictamen = fields.Date(string="Fecha Dictamen:")

    # RADIO BUTTON
    radio = [(
        '1', "Plazo"), ('2', "Objeto"), ('3', "Monto"), ('4', "Monto/Plazo"), ]
    tipo_convenio = fields.Selection(radio, string="Tipo de Convenio:")

    # CONDICION PLAZO
    plazo_fecha_inicio = fields.Date(string="Fecha Inicio:")
    plazo_fecha_termino = fields.Date(string="Fecha Termino:")
    # CONDICION OBJETO
    objeto_nuevo_objeto = fields.Text(string="Objeto:")
    # CONDICION MONTO
    select_monto = [(
        '1', "Ampliación:"), ('2', "Reducción:")]
    tipo_monto = fields.Selection(select_monto, string="Monto:")
    monto_importe = fields.Float(string="Importe:")

    monto_iva = fields.Float(string="I.V.A:", compute="BuscarIva")

    monto_total = fields.Float(string="Total:", compute="sumaMonto")
    # CONDICION MONTO PLAZO
    monto_plazo_fecha_inicio = fields.Date(string="Fecha Inicio:")
    monto_plazo_fecha_termino = fields.Date(string="Fecha Termino:")
    select_monto_plazo = [(
        '1', "Ampliación:"), ('2', "Reducción:")]
    tipo_monto_plazo = fields.Selection(select_monto_plazo, string="Monto:")
    monto_plazo_importe = fields.Float(string="Importe:")

    monto_plazo_iva = fields.Float(string="I.V.A:", compute="BuscarIva")

    monto_plazo_total = fields.Float(string="Total:", compute="sumaMontoPlazo")
    # TERMINA CONDICIONES RADIO BUTTON

    convenio_fecha_fianza = fields.Date(string="Fecha Fianza:")
    convenio_numero_fianza = fields.Integer(string="Numero Fianza:")
    convenio_afianzadora = fields.Char(string="Afianzadora:")
    convenio_monto_afianzadora = fields.Integer(string="Afianzadora:")

    estatus_convenio = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
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

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        return iva

    @api.one
    def nombre(self):
        self.contrato_id = self.id

    @api.depends('monto_importe', 'monto_iva')
    def sumaMonto(self):
        for rec in self:
            rec.update({
                'monto_total': (rec.monto_importe * rec.monto_iva) + rec.monto_importe
            })

    @api.depends('monto_plazo_importe', 'monto_plazo_iva')
    def sumaMontoPlazo(self):
        for rec in self:
            rec.update({
                'monto_plazo_total': (rec.monto_plazo_importe * rec.monto_plazo_iva) + rec.monto_plazo_importe
            })



