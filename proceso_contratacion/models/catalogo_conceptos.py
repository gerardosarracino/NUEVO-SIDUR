# -*- coding: utf-8 -*-

from odoo import api, fields, models


class conceptos_partidas(models.Model):
    _name = "proceso.conceptos_part"
    _rec_name = 'descripcion'

    id_sideop = fields.Integer('ID SIDEOP CATALOGO')

    # verifica si la categoria tiene padre, auxiliar para decorador de tree view
    related_categoria_padre = fields.Many2one('catalogo.categoria', related="categoria.parent_id", store=True)
    # clave
    categoria = fields.Many2one('catalogo.categoria', 'Categoria', )

    descripcion = fields.Text('Descripción')

    name = fields.Many2one('catalogo.categoria', 'Categoria Padre')

    clave_linea = fields.Char('Clave')
    concepto = fields.Text()
    medida = fields.Char()
    precio_unitario = fields.Float()
    cantidad = fields.Float()

    importe = fields.Float(compute="sumaCantidad", store=True)

    # MODIFICACIONES
    fecha_modificacion = fields.Date('Fecha de la Modificación')
    justificacion = fields.Text('Justificación de Modificación')

    # CONCEPTOS EJECUTADOS EN EL PERIODO
    # contratada = fields.Float(string="Contratada",  required=False, compute="test")
    '''est_ant = fields.Integer(string="Est. Ant",  required=False, compute="sumaEst")
    pendiente = fields.Integer(string="Pendiente",  required=False, compute="Pendiente")

    estimacion = fields.Float(string="Estimacion")

    importe_ejecutado = fields.Float(string="Importe",  required=False, compute="importeEjec", store=True)

    '''

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", readonly=True, store=True)

    @api.one
    @api.depends('cantidad', 'estimacion')
    def sumaEst(self):
        for rec in self:
            rec.update({
                'est_ant': rec.cantidad - rec.estimacion
            })

    # VER COMO PROGRAMAREMOS EL ESTIMADO ANTERIOR DE OTRA ESTIMACION DE LA MISMA PROCEDENCIA
    @api.one
    @api.depends('cantidad', 'estimacion')
    def Pendiente(self):
        for rec in self:
            rec.update({
                'pendiente': rec.cantidad - rec.estimacion
            })

    @api.one
    @api.depends('precio_unitario', 'estimacion')
    def importeEjec(self):
        for rec in self:
            rec.update({
                'importe_ejecutado': rec.estimacion * rec.precio_unitario
            })

    @api.one
    @api.depends('precio_unitario', 'cantidad')
    def sumaCantidad(self):
        for rec in self:
            rec.update({
                'importe': rec.cantidad * rec.precio_unitario
            })


class ConceptosModificados(models.Model):
    _name = "proceso.conceptos_modificados"

    obra = fields.Many2one('partidas.partidas', string='Obra:', )

    justificacion = fields.Text('Justificación de Modificación')
    select_tipo = [('1', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:")


class categoria(models.Model):
    _name = "proceso.categoria"
    name = fields.Char()


class concepto(models.Model):
    _name = "proceso.concepto"
    name = fields.Char()


class grupo(models.Model):
    _name = "proceso.grupo"
    name = fields.Char()


class medida(models.Model):
    _name = "proceso.medida"
    name = fields.Char()









