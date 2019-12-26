from odoo import models, fields, api, exceptions


class ControlExpediente(models.Model):
    _name = 'control.expediente'

    tabla_control = fields.Many2many('control_expediente.control_expediente')