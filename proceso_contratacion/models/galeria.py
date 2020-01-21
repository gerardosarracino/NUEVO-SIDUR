from odoo import api, fields, models, tools, _


class Galeria(models.Model):
    _name = 'avance.avance_fisico'
    _rec_name = 'imagen'

    imagen = fields.Binary(string="",  )

    _url = fields.Char(string="")

