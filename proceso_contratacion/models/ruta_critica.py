from odoo import models, fields, api, exceptions

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Frente(models.Model):
    _name = 'proceso.frente'
    _rec_name = 'nombre'
    nombre = fields.Char(string='FRENTE', required=True)


class ruta_critica(models.Model):
    _name = 'proceso.rc'

    id_partida = fields.Many2one('partidas.partidas')
    frente = fields.Many2one('proceso.frente', string='FRENTE')
    obra = fields.Many2one('registro.programarobra')
    name = fields.Char(string="ACTIVIDADES PRINCIPALES", )
    porcentaje_est = fields.Float(string="P.R.C", )
    sequence = fields.Integer()
    avance_fisico = fields.Float(string="% Avance")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)


class ruta_critica_avance(models.Model):
    _name = 'proceso.rc_a'

    frente = fields.Char(string='FRENTE')
    numero_contrato = fields.Many2one('partidas.partidas')
    # actividad = fields.Char(string="ACTIVIDADES PRINCIPALES")
    porcentaje_est = fields.Float(string="P.R.C")
    name = fields.Char(string="ACTIVIDADES PRINCIPALES")
    sequence = fields.Integer()
    avance_fisico = fields.Float(string="% AVANCE")
    obra = fields.Many2one('registro.programarobra')
    r = fields.Many2one('proceso.iavance')
    avance_fisico_ponderado = fields.Float(string="% FISICO PONDERADO", compute='avance_fisico_pon')

    @api.depends('avance_fisico')
    def avance_fisico_pon(self):
        for rec in self:
            rec.update({
                'avance_fisico_ponderado': (rec.porcentaje_est * rec.avance_fisico) / 100
            })

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)


class informe_avance(models.Model):
    _name = 'proceso.iavance'

    ruta_critica = fields.Many2many('proceso.rc_a')
    total_ = fields.Float()
    avance = fields.Float(string="AVANCE %")
    fisico_ponderado = fields.Float(string="FISICO PONDERADO")
    obra = fields.Many2one('registro.programarobra')
    numero_contrato = fields.Many2one('partidas.partidas')
    num_contrato = fields.Char(string='ID contrato sideop')
    porcentaje_e = fields.Float()
    porcentaje_estimado = fields.Float(store=True)
    fecha_actual = fields.Date(string='Fecha', default=fields.Date.today(), required=True)
    comentarios_generales = fields.Text(string='Comentarios generales')
    situacion_contrato = fields.Selection([
        ('bien', "1- Bien"),
        ('satisfactorio', "2- Satisfactorio"),
        ('regular', "3- Regular"),
        ('deficiente', "4- Deficiente"),
        ('mal', "5- Mal")], default='bien', string="Situación del contrato")

    com_avance_obra = fields.Text()

    # aux = fields.Float()

    '''@api.one
    def nombre(self):
        self.contrato_id = self.contrato'''

    @api.multi
    @api.onchange('ruta_critica')
    def suma_importe(self):
        suma = 0
        for i in self.ruta_critica:
            resultado = i.porcentaje_est
            suma += resultado
            self.total_ = suma

    @api.onchange('ruta_critica')
    def porcest(self):
        r_porcentaje_est = 0
        r_avance_fisico = 0
        for i in self.ruta_critica:
            porcentaje_est = i.porcentaje_est
            r_porcentaje_est += porcentaje_est

            avance_fisico = i.avance_fisico
            r_avance_fisico += avance_fisico

            resultado = (r_porcentaje_est * r_avance_fisico) / 100

            self.porcentaje_estimado = float(resultado)

    @api.onchange('obra')  # if these fields are changed, call method
    def conceptosEjecutados(self):
        adirecta_id = self.env['partidas.partidas'].search([('id', '=', self.numero_contrato.id)])[0]
        self.update({
            'ruta_critica': [[5]]
        })
        for conceptos in adirecta_id.ruta_critica:
            self.update({
                'ruta_critica': [[0, 0, {'frente': conceptos.frente, 'name': conceptos.name,
                                         'porcentaje_est': conceptos.porcentaje_est}]]
            })