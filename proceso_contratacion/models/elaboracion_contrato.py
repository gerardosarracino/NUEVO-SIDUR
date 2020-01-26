# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo import api, fields, models, _


class ElaboracionContratos(models.Model):
    _name = "proceso.elaboracion_contrato"
    _rec_name = 'contrato'

    # contador para esconder los pages
    contrato_contador = fields.Integer(compute="contar_contrato")

    @api.one
    def contar_contrato(self):
        b_contrato = self.env['proceso.elaboracion_contrato'].search_count([('id', '=', self.id)])
        self.contrato_contador = b_contrato

    # IMPORTACION
    id_contratista = fields.Char('id contratista')
    id_residente = fields.Char('id _residente')
    num_contrato_sideop = fields.Char('numero contrato sideop')
    id_sideop_partida = fields.Integer('ID SIDEOP part')

    radio_adj_lic = [('1', "Licitación"), ('2', "Adjudicación")]
    tipo_contrato = fields.Selection(radio_adj_lic, string="Tipo de Contrato:", store=True)

    contrato_partida_licitacion = fields.Many2many('partidas.partidas', ondelete="cascade")

    contrato_partida_adjudicacion = fields.Many2many('partidas.partidas', ondelete="cascade")

    # LICITACION PARTIDAS
    obra = fields.Many2one('proceso.licitacion', string="Seleccionar obra")
    # ADJUDICACION PARTIDAS
    adjudicacion = fields.Many2one('proceso.adjudicacion_directa', string="Nombre de Adjudicación", ondelete='cascade')

    # CONTAR REGISTROS DE FINIQUITO
    contar_finiquito = fields.Integer(compute='contar', string="PRUEBA")
    # CONTAR REGISTROS DE CONVENIO
    contar_convenio = fields.Integer(compute='contar2', string="PRUEBA")
    fecha = fields.Date(string="Fecha",  default=fields.Date.today())

    contrato = fields.Char(string="Contrato", related="adjudicacion.numerocontrato", readonly=False, store=True)
    name = fields.Text(string="Descripción/Meta", )

    descripciontrabajos = fields.Text(string="Descripción trabajos:", )
    unidadresponsableejecucion = fields.Many2one('proceso.unidad_responsable', string="Unidad responsable de su "
                                                                                      "ejecución", )
    supervisionexterna = fields.Text(string="Supervisión externa")
    supervisionexterna1 = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:")

    contratista = fields.Many2one('contratista.contratista', compute="b_contratista")

    @api.one
    @api.depends('obra', 'adjudicacion')
    def b_contratista(self):
        if self.tipo_contrato == '2':
            self.contratista = self.adjudicacion.contratista
        elif self.tipo_contrato == '1':
            self.contratista = self.obra.contratista

    fechainicio = fields.Date(string="Fecha de Inicio", )
    fechatermino = fields.Date(string="Fecha de Termino", )
    periodicidadretencion = fields.Selection([('DIARIO', 'DIARIO'),('MENSUAL','MENSUAL'),('ninguno','Ninguno')],
                                             string="Periodicidad Retención",  default='ninguno')
    retencion = fields.Float(string="% Retención")
    # Fianzas
    fianzas = fields.Many2many('proceso.fianza', string="Fianzas:")
    # Deducciones
    deducciones = fields.Many2many("generales.deducciones", string="Deducciones")
    # RECURSOS ANEXOS
    anexos = fields.Many2many('proceso.anexos', string="Anexos:", compute="llenar_anexo", store=True)

    enlace_oficio = fields.Many2one('autorizacion_obra.oficios_de_autorizacion', string="Enlace a Oficio",)
    recurso_autorizado = fields.Float(string='Recursos Autorizados:', related="anexos.name.total_at")
    importe_cancelado = fields.Float(string='Recursos Cancelados:', related="anexos.total_ca")
    total_recurso_aut = fields.Float(string='Total de Recursos Autorizados:', compute="recurso_total")

    # TOTAL DEL CONTRAO Y NUEVO CAMPO TOTAL PARA CONVENIO
    convenios_escalatorias = fields.Float(string="Convenios y Escalatorias:", readonly="True")

    total_contratado = fields.Float(string="Total Contratado:", compute="contratado_total")
    total_contratado_modificado = fields.Float(string="Total Contratado:", compute="contratado_total_modi")

    saldo = fields.Float(string="Saldo:", compute="saldo_total")

    # RELATED CON LA OBRA DE LA PARTIDA PARA RELACIONARLA CON EL ANEXO TECNICO
    obra_partida = fields.Many2one(string="obra partida adjudicacion", related="contrato_partida_adjudicacion.obra")
    obra_partida_licitacion = fields.Many2one(string="obra partida licitacion", related="contrato_partida_licitacion.recursos")
    contrato_id = fields.Char(compute="nombre", store=True)

    # IMPORTE DEL CONTRATO LICITACION Y ADJUDICACION
    impcontra = fields.Float(string="Importe:", compute="importeT")

    estatus_contrato = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_contrato': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_contrato': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_contrato': 'validado'})

    # METODO PARA MANDAR PARAMETRO QUE IDENTIFICAR QUE ADJUDICACION FUE CONTRATADA YA
    @api.model
    def create(self, values):
        # if len(values['adjudicacion']) > 0:
        b_adj = self.env['proceso.adjudicacion_directa'].browse(values['adjudicacion'])
        b_adj.write({'contratado': 1})
        return super(ElaboracionContratos, self).create(values)

    # CONTEXT DESCARGAR ARCHIVO
    @api.multi
    def imprimir_accion(self):
        original_url = "http://sidur.galartec.com/documento/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    '''@api.multi
    def write(self, values):
        b_adj = self.env['proceso.adjudicacion_directa'].browse(self.adjudicacion)
        # b_adj.write({'contratado': 1})
        print(values)
        print('---')
        print(self)
        # values['programa_id'] = str(num)
        return super(ElaboracionContratos, self).write(values)'''

    '''@api.multi
    def unlink(self):
        b_adj = self.env['proceso.adjudicacion_directa'].browse(self.adjudicacion)
        b_adj.write({'contratado': 0})
        return super(ElaboracionContratos, self).unlink()'''

    # METODO PARA CALCULAR EL IMPORTE DEL CONTRATO
    @api.one
    @api.depends('contrato_partida_adjudicacion', 'contrato_partida_licitacion')
    def importeT(self):
        if self.adjudicacion:
            suma = 0
            for i in self.contrato_partida_adjudicacion:
                resultado = i.total_partida
                suma += resultado
                self.impcontra = suma
        else:
            suma = 0
            for i in self.contrato_partida_licitacion:
                resultado = i.total_partida
                suma += resultado
                self.impcontra = suma

    # VALIDACIONES DE FECHAS
    @api.onchange('fechatermino')
    @api.depends('fechatermino', 'fechainicio')
    def onchange_fechatermino(self):
        if str(self.fechatermino) < str(self.fechainicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la fecha de inicio, '
                                     'por favor seleccione una fecha posterior')
        else:
            return False

    @api.onchange('fechainicio')
    @api.depends('fechatermino', 'fechainicio')
    def onchange_fechainicio(self):
        if str(self.fechatermino) < str(self.fechainicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha posterior a la de termino, '
                                     'por favor seleccione una fecha anterior')
        else:
            return False

    # VALIDACIONES DE RECURSOS
    '''@api.onchange('impcontra')
    def onchange_recursos(self):
        if self.saldo < 0:
            raise exceptions.Warning('No se cuenta con los recursos suficientes')
        else:
            return False'''

    # METODO PARA INYECTAR ANEXOS
    @api.one
    @api.depends('adjudicacion', 'obra')
    def llenar_anexo(self):
        b_anexo = self.env['autorizacion_obra.anexo_tecnico'].search([('id', '=', self.obra_partida.id or
                                                                       self.obra_partida_licitacion.id)])
        self.update({
            'anexos': [[5]]
        })
        for anexos_b in b_anexo:
            self.update({
                'anexos': [[0, 0, {'name': anexos_b.name, 'claveobra': anexos_b.claveobra,
                                   'id_contrato': self.id,
                                   'clave_presupuestal': anexos_b.clave_presupuestal,
                                   'federal': anexos_b.federal,
                                   'concepto': anexos_b.concepto,
                                   'estatal': anexos_b.estatal,
                                   'municipal': anexos_b.municipal, 'otros': anexos_b.otros,
                                   'ferderalin': anexos_b.federalin, 'estatalin': anexos_b.estatalin,
                                   'municipalin': anexos_b.municipalin, 'otrosin': anexos_b.otrosin,
                                   'total': anexos_b.total, 'cancelados': anexos_b.cancelados,
                                   'total_ca': anexos_b.total_ca,
                                   'total1': anexos_b.total1, 'totalin': anexos_b.totalin,
                                   'total_at': anexos_b.total_at,
                                      }]]
            })

    '''@api.one
    def contar_convenios(self):
        count = self.env['proceso.convenios_modificado'].search_count([('contrato', '=', self.contrato)])
        self.contador_convenios = count'''

    @api.depends('total_recurso_aut', 'total_contratado')
    def saldo_total(self):
        for rec in self:
            rec.update({
                'saldo': rec.total_recurso_aut - rec.total_contratado
            })

    @api.depends('impcontra')
    def contratado_total(self):
        for rec in self:
            rec.update({
                'total_contratado': rec.impcontra
            })



    @api.depends('impcontra', 'convenios_escalatorias')
    def contratado_total_modi(self):
        for rec in self:
            rec.update({
                'total_contratado': rec.impcontra + rec.convenios_escalatorias
            })

    # CALCULAR EL RECURSO TOTAL DE LOS ANEXOS
    @api.depends('recurso_autorizado', 'importe_cancelado')
    def recurso_total(self):
        for rec in self:
            rec.update({
                'total_recurso_aut': rec.recurso_autorizado - rec.importe_cancelado
            })

    # IDS DE REFERENCIA DE LA ADJUDICACION O LICITACION PARA METODO DE BUSCAR CONTRATO EN PARTIDAS
    id_ad = fields.Integer(string="ID DE LA ADJUDICACION RELACION", related="adjudicacion.id")
    id_lic = fields.Integer(string="ID DE LA LICITACION RELACION", related="obra.id")

    # METODO DE LAS PARTIDAS ADJUDICACION
    @api.multi
    @api.onchange('adjudicacion')  # if these fields are changed, call method
    def check_change_adjudicacion(self):
        adirecta_id = self.env['proceso.adjudicacion_directa'].browse(self.adjudicacion.id)
        self.update({
            'contrato_partida_adjudicacion': [[5]]
        })
        cont = 0
        for partidas in adirecta_id.programar_obra_adjudicacion:
            cont = cont + 1
            self.update({
                'contrato_partida_adjudicacion': [[0, 0, {'obra': partidas.obra,
                                                          'programaInversion': partidas.programaInversion,
                                                          'monto_partida': partidas.monto_partida,
                                                          'iva_partida': partidas.iva_partida,
                                                          'total_partida': partidas.total_partida,
                                                          'nombre_partida': self.contrato,
                                                          'p_id': cont,
                                                          'id_contrato_relacion': str(self.id_ad),
                                                          }]]
                     })

    # METODO DE LAS PARTIDAS LICITACION
    @api.multi
    @api.onchange('obra')  # if these fields are changed, call method
    def check_change_licitacion(self):
        adirecta_id = self.env['proceso.licitacion'].browse(self.obra.id)
        self.update({
            'contrato_partida_licitacion': [[5]]
        })
        cont = 0
        for partidas in adirecta_id.programar_obra_licitacion:
            cont = cont + 1
            self.update({
                'contrato_partida_licitacion': [[0, 0, {'recursos': partidas.recursos,
                                                          'programaInversion': partidas.programaInversion,
                                                          'obra': partidas.obra,
                                                          'monto_partida': partidas.monto_partida,
                                                          'iva_partida': partidas.iva_partida,
                                                          'total_partida': partidas.total_partida,
                                                          'nombre_partida': self.contrato,
                                                          'p_id': cont,
                                                          'id_contrato_relacion': str(self.id_lic)
                                                        }]]
            })

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def contar(self):
        count = self.env['proceso.finiquitar_anticipadamente'].search_count([('contrato', '=', self.id)])
        self.contar_finiquito = count

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def contar2(self):
        count = self.env['proceso.convenios_modificado'].search_count([('contrato', '=', self.id)])
        self.contar_convenio = count

    # METODO DE ENLACE
    @api.one
    def nombre(self):
        self.contrato_id = self.contrato

    # CONVENIOS MODIFICATORIOS METODOS DE ABRIR VENTANA EN MODO NEW Y EN TREE VIEW
    @api.multi
    def conveniosModificados1(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios Modificatorios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'form,tree',
            'target': 'new',
        }

    @api.multi
    def conveniosModificados2(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios Modificatorios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'tree,form',
        }

    # FINIQUITAR CONTRATO METODOS DE ABRIR VENTANA EN MODO NEW Y EN TREE VIEW
    @api.multi
    def finiquitarContrato1(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Finiquitar Contrato Anticipadamente',
            'res_model': 'proceso.finiquitar_anticipadamente',
            'view_mode': 'form,tree',
            'target': 'new',
        }

    @api.multi
    def finiquitarContrato2(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Finiquitar Contrato Anticipadamente',
            'res_model': 'proceso.finiquitar_anticipadamente',
            'view_mode': 'tree,form',
        }

    #
    @api.multi
    def Seleccion(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccion de Obra',
            'res_model': 'proceso.elaboracion_contrato',
            'view_type': 'form',
            'target': 'new',
        }


class AnexosAuxiliar(models.Model):
    _name = 'proceso.anexos'

    id_contrato = fields.Many2one('proceso.elaboracion_contrato')

    name = fields.Many2one('autorizacion_obra.oficios_de_autorizacion')

    fecha_de_recibido = fields.Date(string='Fecha de recibido', related="name.fecha_de_recibido")
    fecha_de_vencimiento = fields.Date(string='Fecha de vencimiento', related="name.fecha_de_vencimiento")

    concepto = fields.Many2one('registro.programarobra')
    claveobra = fields.Char(string='Clave de obra')
    clave_presupuestal = fields.Char(string='Clave presupuestal')
    federal = fields.Float(string='Federal')
    estatal = fields.Float(string='Estatal')
    municipal = fields.Float(string='Municipal')
    otros = fields.Float(string='Otros')
    federalin = fields.Float(string='Federal')
    estatalin = fields.Float(string='Estatal')
    municipalin = fields.Float(string='Municipal')
    otrosin = fields.Float(string='Otros')
    total = fields.Float()
    cancelados = fields.Integer()
    total_ca = fields.Float(string='Cancelado')
    total1 = fields.Float(string="Total")
    totalin = fields.Float(string="Indirectos")

    total_at = fields.Float()


class UnidadResponsableEjecucion(models.Model):
    _name = 'proceso.unidad_responsable'

    name = fields.Char('Descripción:')


class Fianza(models.Model):
    _name = 'proceso.fianza'

    select_tipo_fianza = [('1', 'Cumplimiento'), ('2', 'Calidad/Vicios Ocultos'), ('3', 'Responsabilidad Civil'),
                          ('4', 'Ninguno')]
    tipo_fianza = fields.Selection(select_tipo_fianza, string="Tipo Fianza", default="4", )
    numero_fianza_fianzas = fields.Char(string="Numero Fianza", )
    monto = fields.Float(string="Monto", )
    fecha_fianza_fianzas = fields.Date(string="Fecha Fianza", )
    afianzadora_fianzas = fields.Char(string="Afianzadora", )


class FiniquitarContratoAnticipadamente(models.Model):
    _name = "proceso.finiquitar_anticipadamente"

    @api.one
    def nombre(self):
        self.contrato_id = self.id

    contrato_id = fields.Char(compute="nombre", store=True)
    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Numero Contrato:', readonly=True)

    fecha = fields.Date(string="Fecha:")
    referencia = fields.Char(string="Referencia:")
    observaciones = fields.Text(string="Observaciones:")


