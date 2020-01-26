from odoo import models, fields, api, exceptions


class EstadoObra(models.Model):
    _name = 'semaforo.estado_obra'

    partidaid = fields.Many2one('partidas.partidas')
    fecha = fields.Date(string="Fecha", required=False, )
    descripcion = fields.Text(string="Decripción", required=False, )

    select_estado = [('1', 'Terminado'), ('2', 'En Ejecucion'), ('3', 'Sin Anticipo'),
                          ('4', 'Terminado Anticipadamente'), ('5', 'Rescindido'), ('6', 'En Observacion'),
                     ('7', 'Nueva'), ('8', 'Fuera de Semaforo'), ('9', 'Falta Doc_cierre')]
    tipo_estado = fields.Selection(select_estado, string="Estado")


class Actividad(models.Model):
    _name = 'semaforo.actividad'

    partidaid = fields.Many2one('partidas.partidas')
    titulo = fields.Char(string="Título", required=False, )
    contenido = fields.Text(string="Decripción", required=False, )

    fecha = fields.Date(string="Fecha de vencimiento", required=False, )

    select_estado = [('1', 'Abierto'), ('2', 'Cerrado'), ('3', 'Cancelado')]
    tipo_estado = fields.Selection(select_estado, string="Estado", default=1)