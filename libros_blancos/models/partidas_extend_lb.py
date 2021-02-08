# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.odoo import api


class PartidasLb(models.Model):
    _inherit = 'partidas.partidas'

    

    '''@api.multi
    def registro_entrega(self):
        # VISTA OBJETIVO
        view = self.env.ref('libros_blancos.entrega_documentos_checklist')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registro de Entrega',
            'res_model': 'lb.entrega_documentos',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_p_id': self.id},
            'view_id': view.id,
        }'''
