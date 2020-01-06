from odoo import models, fields, api, exceptions


class ControlExpediente(models.Model):
    _name = 'control.expediente'

    # PARTIDA ENLACE
    p_id = fields.Many2one(comodel_name="partidas.partidas", string="ENLACE A PARTIDAS", required=False, store=True)

    # tabla_control = fields.Many2many('control_expediente.control_expediente')

    select_etapa = [('1', 'PREVIO AL PROCESO DE CONTRATACIÓN'), ('2', 'DURANTE EL PROCESO DE CONTRATACIÓN'),
                    ('3', 'DESPUÉS DEL PROCEDIMIENTO DE CONTRATACIÓN Y ANTES DE EJECUTAR LA OBRA'),
                    ('4', 'DURANTE LA EJECUCIÓN DE LA OBRA'), ('5', 'DESPUÉS DE LA EJECUCIÓN DE LA OBRA')]

    etapa = fields.Selection(select_etapa, string="Etapa:", store=True)

    responsable = fields.Many2one(
        comodel_name='res.users',
        string='Responsable:',
        default=lambda self: self.env.user.id,
        required=True
    )
    nombre = fields.Many2one('control_expediente.control_expediente', string="Nombre:", store=True)

    orden = fields.Char(string="Orden:", )

    referencia = fields.Char(string="Referencia", required=False, )

    fecha = fields.Date(string="Fecha", required=False, )

    aplica = fields.Boolean(string="No Aplica",  )
    existe = fields.Boolean(string="Existe",  )

    comentarios = fields.Text(string="Comentarios", required=False, )

    documento = fields.Binary(string="",  )
    nombre_documento = fields.Char(string="Nombre del Documento", required=False, )

    # METODO PARA INGRESAR A RECURSOS BOTON
    @api.multi
    def vista_expediente(self):
        # VISTA OBJETIVO
        view = self.env.ref('control_expediente.form_control_expediente')
        # CONTADOR SI YA FUE CREADO
        count = self.env['control.expediente'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['control.expediente'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Control Expediente',
                'res_model': 'control.expediente',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search[0].id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Control Expediente',
                'res_model': 'control.expediente',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }
