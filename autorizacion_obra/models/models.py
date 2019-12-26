from odoo import models, fields, api
from datetime import datetime


class AutorizacionDeObra(models.Model):
    _name = 'autorizacion_obra.oficios_de_autorizacion'
    _rec_name = 'id_sideop'

    id_sideop = fields.Integer('id sideop')

    name = fields.Char(string='Número de oficio', )
    fecha_actual = fields.Date(string='Fecha',default=fields.Date.today(), )
    fecha_de_recibido = fields.Date(string='Fecha de recibido', )
    fecha_de_vencimiento = fields.Date(string='Fecha de vencimiento', )
    importe = fields.Float(string='Importe', )
    anexo_tec = fields.Integer(compute='contar')
    total_at = fields.Float(compute='suma_total_anexos')
    anexos = fields.One2many('autorizacion_obra.anexo_tecnico', 'name')
    total_atcancel = fields.Float(string='Importe anexos', compute='suma_total_cancel')

    @api.one
    def suma_total_anexos(self):
        ids = self.env['autorizacion_obra.anexo_tecnico'].search([('name', '=', self.id)])
        suma = 0
        for i in ids:
            resultado = self.env['autorizacion_obra.anexo_tecnico'].browse(i.id).total
            suma += float(resultado)
        self.total_at = suma

    @api.one
    def suma_total_cancel(self):
        ids1 = self.env['autorizacion_obra.anexo_tecnico'].search([('name', '=', self.id)])
        suma1 = 0
        for i in ids1:
            resultado1 = self.env['autorizacion_obra.anexo_tecnico'].browse(i.id).total1
            suma1 += float(resultado1)
        self.total_atcancel = suma1

    @api.one
    def contar(self):
        count = self.env['autorizacion_obra.anexo_tecnico'].search_count([('name', '=', self.id)])
        self.anexo_tec = count


class AnexoTecnico(models.Model):
    _name = 'autorizacion_obra.anexo_tecnico'
    _rec_name = 'id'

    id_anexo_sideop = fields.Integer('id anexo sideop')
    id_partida_sideop = fields.Integer('id partida sideop')
    id_oficio_sideop = fields.Integer('id oficio sideop')

    name = fields.Many2one('autorizacion_obra.oficios_de_autorizacion', ondelete="cascade")

    # PROGRAMA DE INVERSION AUXILIAR
    # p_inv = fields.Many2one('generales.programas_inversion', related="concepto.programaInversion")

    claveobra = fields.Char(string='Clave de obra', )
    clave_presupuestal = fields.Char(string='Clave presupuestal', )
    concepto = fields.Many2one('registro.programarobra', )
    federal = fields.Float(string='Federal')
    estatal = fields.Float(string='Estatal')
    municipal = fields.Float(string='Municipal')
    otros = fields.Float(string='Otros')
    federalin = fields.Float(string='Federal')
    estatalin = fields.Float(string='Estatal')
    municipalin = fields.Float(string='Municipal')
    otrosin = fields.Float(string='Otros')
    total = fields.Float(compute="_total", store=True)
    cancelados = fields.Integer(compute='contar')
    total_ca = fields.Float(string='Cancelado',compute='suma_total_cancelado')
    total1 = fields.Float(string="Total", compute="_total1")
    totalin = fields.Float(string="Indirectos", compute="_totalin")
    cancelado = fields.One2many('autorizacion_obra.cancelarrecurso', 'name')

    total_at = fields.Float(compute='suma_total_anexos')

    @api.one
    def suma_total_anexos(self):
        ids = self.env['autorizacion_obra.anexo_tecnico'].search([('name', '=', self.id)])
        suma = 0
        for i in ids:
            resultado = self.env['autorizacion_obra.anexo_tecnico'].browse(i.id).total
            suma += float(resultado)
        self.total_at = suma

    @api.depends('federal','estatal','municipal','otros','federalin','estatalin','municipalin','otrosin')
    def _total(self):
        for r in self:
            r.total = (r.federal + r.estatal + r.municipal + r.otros) + (r.federalin + r.estatalin + r.municipalin + r.otrosin)

    @api.depends('federalin','estatalin','municipalin','otrosin')
    def _totalin(self):
        for r in self:
            r.totalin = r.federalin + r.estatalin + r.municipalin + r.otrosin

    @api.depends('total','total_ca')
    def _total1(self):
        for r in self:
            r.total1 = r.total - r.total_ca

    @api.one
    def suma_total_cancelado(self):
        ids = self.env['autorizacion_obra.cancelarrecurso'].search([('name', '=', self.id)])
        suma = 0
        for i in ids:
            resultado = self.env['autorizacion_obra.cancelarrecurso'].browse(i.id).totalc
            suma += float(resultado)
        self.total_ca = suma

    @api.one
    def contar(self):
        count = self.env['autorizacion_obra.cancelarrecurso'].search_count([('name', '=', self.id)])
        self.cancelados = count


class CancelacionRecursos(models.Model):
    _name = 'autorizacion_obra.cancelarrecurso'

    name = fields.Many2one('autorizacion_obra.anexo_tecnico', 'id', readonly=True, ondelete="cascade")
    nooficio = fields.Char(string="No. Oficio", )
    fecha = fields.Date(string="Fecha", )
    federalc = fields.Float(string='Federal')
    estatalc = fields.Float(string='Estatal')
    municipalc = fields.Float(string='Municipal')
    otrosc = fields.Float(string='Otros')
    federalcin = fields.Float(string='Federal')
    estatalcin = fields.Float(string='Estatal')
    municipalcin = fields.Float(string='Municipal')
    otroscin = fields.Float(string='Otros')
    totalcin = fields.Float(compute="_totalcin", store=True)
    totalc = fields.Float(compute="_totalc", store=True)

    @api.depends('federalc','estatalc','municipalc','otrosc','federalcin','estatalcin','municipalcin','otroscin')
    def _totalc(self):
        for c in self:
            c.totalc = c.federalc + c.estatalc + c.municipalc + c.otrosc + c.federalcin + c.estatalcin + c.municipalcin + c.otroscin

    @api.depends('federalcin','estatalcin','municipalcin','otroscin')
    def _totalcin(self):
        for r in self:
            r.totalcin = r.federalcin + r.estatalcin + r.municipalcin + r.otroscin