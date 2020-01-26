# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class Licitacion(models.Model):
    _name = "proceso.licitacion"
    _rec_name = 'numerolicitacion'

    licitacion_id = fields.Char(compute="nombre", store=True)

    contratista = fields.Many2one('contratista.contratista', 'Contratista Ganador', compute="b_ganador")

    @api.one
    def b_ganador(self):
        b_ganador = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.id)])
        for i in b_ganador:
            if i.ganador is True:
                self.contratista = i.name
            else:
                print('No se encontró ganador')

    # PROGRAMA DE INVERSION
    programa_inversion_licitacion = fields.Many2one('generales.programas_inversion', 'Programa de Inversión')

    # OBRA / RECURSO A LICITAR
    programar_obra_licitacion = fields.Many2many("partidas.licitacion", string="Partida(s):", ondelete="cascade")

    name = fields.Text(string="Objeto De La Licitación", related="programar_obra_licitacion.recursos.concepto.descripcion")
    select = [('1', 'Licitación publica'), ('2', 'Licitación simplificada/Por invitación')]
    tipolicitacion = fields.Selection(select, string="Tipo de Licitación", default="1", )

    numerolicitacion = fields.Char(string="Número de Licitación", )

    estado_obra_desierta = fields.Integer(compute='estadoObraDesierta')
    estado_obra_cancelar = fields.Integer(compute='estadoObraCancelar')

    convocatoria = fields.Char(string="Convocatoria", )
    fechaconinv = fields.Date(string="Fecha Con/Inv", )
    select1 = [('1', 'Estatal'), ('2', 'Nacional'), ('3', 'Internacional')]
    caracter = fields.Selection(select1, string="Carácter", default="1", )
    select2 = [('1', 'Federal'), ('2', 'Estatal')]
    normatividad = fields.Selection(select2, string="Normatividad", required=True )
    # funcionariopresideactos = fields.Char(string="Funcionario que preside actos", )
    funcionariopresideactos = fields.Many2one(
        comodel_name='res.users',
        string='Funcionario que preside actos')
    puesto = fields.Text(string="Puesto", )
    numerooficio = fields.Char(string="Numero oficio", )
    fechaoficio = fields.Date(string="Fecha oficio", )
    oficioinvitacioncontraloria = fields.Char(string="Oficio invitación contraloría", )
    fechaoficio2 = fields.Date(string="Fecha oficio", )
    notariopublico = fields.Text(string="Notario publico", )
    fechalimiteentregabases = fields.Date(string="Fecha Límite para la entrega de Bases", )
    fecharegistrocompranet = fields.Date(string="Fecha Registro CompraNet", )
    costobasesdependencia = fields.Float(string="Costo de Bases Dependencia", )
    costocompranetbanco = fields.Float(string="Costo CompraNET/Banco",)
    fechaestimadainicio = fields.Date(string="Fecha Estimada de Inicio", )
    fechaestimadatermino = fields.Date(string="Fecha Estimada de Termino", )

    plazodias = fields.Integer(string="Plazo de Días", compute="calcular_dias")

    @api.one
    @api.depends('fechaestimadainicio', 'fechaestimadatermino')
    def calcular_dias(self):
        if self.fechaestimadainicio and self.fechaestimadatermino is False:
            self.plazodias = 0
        elif self.fechaestimadainicio and self.fechaestimadatermino:
            f1 = datetime.strptime(str(self.fechaestimadainicio), "%Y-%m-%d")
            f2 = datetime.strptime(str(self.fechaestimadatermino), "%Y-%m-%d")
            r = f2 - f1
            self.plazodias = r.days

    capitalcontable = fields.Float(string="Capital Contable",)
    anticipomaterial = fields.Float(string="Anticipo Material %")
    anticipoinicio = fields.Float(string="Anticipo Inicio %")
    puntosminimospropuestatecnica = fields.Char(string="Puntos mínimos propuesta técnica")
    visitafechahora = fields.Datetime(string="Fecha/Hora")
    visitalugar = fields.Text(string="Lugar")
    juntafechahora = fields.Datetime(string="Fecha/Hora")
    juntalugar = fields.Text(string="Lugar")
    aperturafechahora = fields.Datetime(string="Fecha/Hora")
    aperturalugar = fields.Text(string="Lugar")
    fallofechahora = fields.Datetime(string="Fecha/Hora")
    fallolugar = fields.Text(string="Lugar")

    select3 = [('1', 'EN PROCESO, RECIEN CREADA'), ('2', 'Apertura de preposiciones'), ('3', 'Junta de aclaraciones'),
               ('4', 'Licitación enviada para su contratación')]

    estatus = fields.Selection(select3, string="Estatus de Licitación", default="1", compute="estatus_licitaciones")

    # ESTADO DE LA LICITACION
    @api.one
    def estatus_licitaciones(self):
        b_eventos = self.env['proceso.eventos_licitacion'].search([('numerolicitacion_evento.id', '=', self.id)])
        b_participantes = self.env['proceso.participante'].search_count([('numerolicitacion.id', '=', self.id)])
        if b_participantes >= 1:
            print('asies')
        for i in b_eventos.contratista_aclaraciones:
            if i.asiste:
                self.estatus = '3'
            else:
                self.estatus = '1'

    variable_count = fields.Integer(compute='contar')

    estatus_licitacion = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    # METODO PARA INGRESAR A EVENTOS
    @api.multi
    def VentanaEventos(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_eventos_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.eventos_licitacion'].search_count([('numerolicitacion_evento.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.eventos_licitacion'].search([('numerolicitacion_evento.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Eventos',
                'res_model': 'proceso.eventos_licitacion',
                'view_mode': 'form',
                'target': 'self',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Eventos',
                'res_model': 'proceso.eventos_licitacion',
                'view_mode': 'form',
                'target': 'self',
                'view_id': view.id,
            }

    # METODO PARA INGRESAR A PARTICIPANTES
    @api.multi
    def VentanaParticipantes(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_participantes_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.participante'].search_count([('numerolicitacion.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.participante'].search([('numerolicitacion.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Participantes',
                'res_model': 'proceso.participante',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Participantes',
                'res_model': 'proceso.participante',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_licitacion': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_licitacion': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_licitacion': 'validado'})

    @api.multi
    @api.onchange('programas_inversion_adjudicacion')
    def BorrarTabla(self):
        self.update({
            'programar_obra_adjudicacion': [[5]]
        })

    # METODO CONTADOR DE PARTICIPANTES
    @api.one
    def contar(self):
        b = self.env['proceso.participante'].search([('numerolicitacion', '=', self.id)])
        acum = 0
        for i in b.contratista_participantes:
            acum = acum + 1
        self.variable_count = acum

    # METODO DE OBRA DESIERTA
    @api.one
    def estadoObraDesierta(self):
        resultado = self.env['proceso.estado_obra_desierta'].search_count([('numerolicitacion', '=', self.id)])
        self.estado_obra_desierta = resultado

    # METODO DE OBRA CANCELADA
    @api.one
    def estadoObraCancelar(self):
        resultado = self.env['proceso.estado_obra_cancelar'].search_count([('numerolicitacion', '=', self.id)])
        self.estado_obra_cancelar = resultado

    # ENLACE CON LA LICITACION
    @api.one
    def nombre(self):
        self.licitacion_id = self.numerolicitacion


# EVENTOS DE LICITACION
class Eventos(models.Model):
    _name = 'proceso.eventos_licitacion'
    _rec_name = 'numerolicitacion_evento'

    licitacion_id = fields.Char(compute="nombre", store=True, ondelete="cascade")

    numerolicitacion_evento = fields.Many2one('proceso.licitacion', string='Numero Licitación:', readonly=True,
                                              store=True, ondelete="cascade")

    contratista_participantes = fields.Many2many('proceso.contra_participantev', store=True, ondelete="cascade")
    contratista_aclaraciones = fields.Many2many('proceso.contra_aclaraciones', store=True, ondelete="cascade")
    contratista_propuesta = fields.Many2many('proceso.contra_propuestas', store=True, ondelete="cascade")
    contratista_fallo = fields.Many2many('proceso.contra_fallo', compute="llenar_fallo", store=True, ondelete="cascade")

    # AUXILIAR PARA ACCIONAR METODO
    aux = fields.Float(string="aux",  required=False, )

    # METODO PARA INGRESAR A DATOS GENERALES DEL FALLO
    @api.multi
    def dato_fallo(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_fallo_datos_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.datos_fallo'].search_count([('id_eventos.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.datos_fallo'].search([('id_eventos.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.datos_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.datos_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }

    @api.one
    def nombre(self):
        self.licitacion_id = self.id

    # METODO PARA LLENAR TABLA CON DATOS DE LOS PARTICIPANTES VISITA OBRA
    @api.multi
    @api.onchange('aux')
    def llenar_evento(self):
        b_participante = self.env['proceso.participante'].search([('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
        self.update({
            'contratista_participantes': [[5]]
        })
        for i in b_participante.contratista_participantes:
            self.update({
                'contratista_participantes': [[0, 0, {'name': i.id, 'nombre_representante': i.nombre_representante,
                                                      'correo': i.correo}]]
            })

    # METODO PARA LLENAR TABLA CON DATOS DE LOS PARTICIPANTES JUNTA ACLARACIONES
    @api.multi
    @api.onchange('aux')
    def llenar_aclaraciones(self):
        b_participante = self.env['proceso.participante'].search(
            [('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
        self.update({
            'contratista_aclaraciones': [[5]]
        })
        for i in b_participante.contratista_participantes:
            self.update({
                'contratista_aclaraciones': [
                    [0, 0, {'name': i.id, 'nombre_representante': i.nombre_representante,
                            'correo': i.correo, 'licitacion_id': self.numerolicitacion_evento.id}]]
            })

    # METODO PARA LLENAR TABLA CON DATOS DE LOS PARTICIPANTES APERTURA DE PROPUESTA
    @api.multi
    @api.onchange('aux')
    def llenar_propuesta(self):
        b_participante = self.env['proceso.participante'].search(
            [('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])

        self.update({
            'contratista_propuesta': [[5]]
        })

        id_lic = b_participante.numerolicitacion

        for i in b_participante.contratista_participantes:
            self.update({
                'contratista_propuesta': [
                    [0, 0, {'name': i.id, 'nombre_representante': i.nombre_representante, 'numerolicitacion': id_lic.id,

                            }]]
            })

    # METODO PARA LLENAR TABLA CON DATOS DE LOS PARTICIPANTES FALLO DE LICITACION
    @api.one
    @api.depends('aux')
    def llenar_fallo(self):
        b_participante = self.env['proceso.participante'].search(
            [('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
        self.update({
            'contratista_fallo': [[5]]
        })
        id_lic = b_participante.numerolicitacion
        for i in b_participante.contratista_participantes:
            self.update({
                'contratista_fallo': [
                    [0, 0, {'name': i.id, 'numerolicitacion': id_lic}]]
            })


# VISITA DE OBRA
class ContratistaParticipanteV(models.Model):
    _name = 'proceso.contra_participantev'

    name = fields.Many2one('contratista.contratista', 'Contratista')
    # name = fields.Char(string="Licitante:")
    nombre_representante = fields.Char(string="Nombre del Representante:")
    correo = fields.Char(string="Correo:")
    asiste = fields.Boolean('Asiste')


# JUNTA ACLARACIONES
class JuntaAclaraciones(models.Model):
    _name = 'proceso.contra_aclaraciones'

    licitacion_id = fields.Many2one('proceso.licitacion', readonly=True)
    # name = fields.Char(string="Licitante:")
    name = fields.Many2one('contratista.contratista', 'Contratista')
    nombre_representante = fields.Char(string="Nombre del Representante:")
    correo = fields.Char(string="Correo:")
    asiste = fields.Boolean('Asiste')

    preguntas = fields.Many2many("proceso.preguntas", string="Preguntas del Licitante")

    # METODO PARA INGRESAR A ACLARACIONES
    @api.multi
    def aclaraciones(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_aclaraciones_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_aclaraciones'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_aclaraciones'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Preguntas',
                'res_model': 'proceso.contra_aclaraciones',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Preguntas',
                'res_model': 'proceso.contra_aclaraciones',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }


# CLASE DE PREGUNTAS DE ACLARACIONES
class Preguntas(models.Model):
    _name = 'proceso.preguntas'

    pregunta = fields.Char(string="Pregunta:", required=False, )
    respuesta = fields.Text(string="Respuesta:", required=False, )


# Apertura de Propuestas
class AperturaPropuestas(models.Model):
    _name = 'proceso.contra_propuestas'

    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:')

    # name = fields.Char(string="Licitante:", )
    name = fields.Many2one('contratista.contratista', 'Contratista')

    monto = fields.Float(string="Monto:", readonly=True)
    asiste = fields.Boolean('Asiste')
    completa = fields.Boolean('Completa')
    revision = fields.Boolean('Para revisión')
    puntos_tecnicos = fields.Float('Puntos Tecnicos')
    puntos_economicos = fields.Float('Puntos Economicos')
    paso = fields.Boolean('Pasó')

    posicion = fields.Selection([('1', 'Posición #1')], 'Posición')

    programar_obra_licitacion2 = fields.Many2many("proceso.propuesta_lic", string="Partida(s):", store=True)

    aux = fields.Float(string="aux", required=False, )

    observaciones = fields.Text(string="Observaciones:", required=False, )

    # AUXILIAR PARA ACCIONAR METODO

    # SUMA DE LOS MONTOS
    @api.multi
    @api.onchange('programar_obra_licitacion2')
    def sumMonto(self):
        sum = 0
        for i in self.programar_obra_licitacion2:
            sum = sum + i.monto_partida
            self.monto = sum

    # METODO PARA TRAER LA OBRA DE LA LICITACION PARA ASIGNAR RECURSO

    @api.multi
    @api.onchange('numerolicitacion', 'id')
    def llenar_licitacion_r(self):

        print('PRUEBA METODOOO AQUIIII')

        if self.programar_obra_licitacion2 is None:
            print('si')
            b_lic = self.env['proceso.licitacion'].search(
                [('id', '=', self.numerolicitacion.id)])
            for i in b_lic.programar_obra_licitacion:
                self.update({
                    'programar_obra_licitacion2': [[0, 0, {'recursos': i.recursos,
                                                           'licitacion_id': self.numerolicitacion.id}]]
                })
        else:
            print('xfvdscg')

    # METODO PARA INGRESAR A PROPUESTAS BOTON
    @api.multi
    def propuestas(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_propuesta_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_propuestas'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_propuestas'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Propuesta',
                'res_model': 'proceso.contra_propuestas',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Propuesta',
                'res_model': 'proceso.contra_propuestas',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }


# FALLO DE LICITACIONES
class Fallo(models.Model):
    _name = 'proceso.contra_fallo'

    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:')
    id_eventos = fields.Many2one('proceso.eventos_licitacion', string='id evento:',required=True)

    # name = fields.Char(string="Licitante:")
    name = fields.Many2one('contratista.contratista', 'Contratista')
    monto = fields.Float(string="Monto Fallado A/I.V.A:", compute="b_monto")
    posicion = fields.Selection([('1', 'Posición #1')], 'Posición', compute="b_monto")
    nombre_representante = fields.Char(string="Nombre del Representante:")

    # METODO PARA TRAER LOS DATOS DEL MONTO Y POSICION DE LA PROPUESTA
    @api.one
    def b_monto(self):
        b_mont = self.env['proceso.contra_propuestas'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        acum = 0
        for i in b_mont:
            if int(i.name.id) == int(self.name.id):
                print('PRUEBA')
                if i.posicion:
                    for x in i.programar_obra_licitacion2:
                        acum += x.monto_partida
                    self.monto = acum
                    self.posicion = i.posicion
                else:
                    print('No se encontró monto de propuesta')
            else:
                print('no')

    asiste = fields.Boolean('Asistió')
    ganador = fields.Boolean('Ganador')
    puntos_tecnicos = fields.Float('Puntos Tecnicos')
    puntos_economicos = fields.Float('Puntos Economicos')

    observaciones = fields.Text(string="Observaciones")

    contador_ganador = fields.Integer(compute="ganador_count")

    # METODO PARA VERIFICAR SI YA HAY GANADOR, PARA ATRIBUTO READONLY EN LA VISTA
    @api.one
    def ganador_count(self):
        print('GANADOR ALV')
        b_fallo = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        for i in b_fallo:
            print(i.ganador)
            if i.ganador is True:
                self.contador_ganador = 1

    # METODO PARA INGRESAR A FALLO BOTON
    @api.multi
    def fallo(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_fallo_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_fallo'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_fallo'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.contra_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.contra_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }


# VENTANA DE DATOS DEL FALLO
class DatosFallo(models.Model):
    _name = 'proceso.datos_fallo'
    _rec_name = 'ganador'

    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:', readonly=True, store=True)
    id_eventos = fields.Many2one('proceso.eventos_licitacion', string='id evento:',required=True)

    # ganador = fields.Char(string="Ganador:", compute="b_ganador")
    ganador = fields.Many2one('contratista.contratista', 'Contratista', compute="b_ganador")

    @api.one
    def b_ganador(self):
        b_ganador = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        for i in b_ganador:
            if i.ganador is True:
                self.importe_ganador = i.monto
                self.ganador = i.id
            else:
                print('No se encontró ganador')

    fecha_fallo = fields.Date(string="Fecha Fallo:")
    hora_inicio_f = fields.Datetime(string="Hora de Inicio Fallo:")
    hora_termino_f = fields.Datetime('Hora Termino Fallo:')
    hora_inicio_o = fields.Date('Fecha Inicio Obra:')
    hora_termino_o = fields.Date('Fecha Termino Obra:')
    plazo = fields.Integer('Plazo')
    hora_antes_firma = fields.Datetime('Hora Antes Firma Contrato:')
    fecha_fcontrato = fields.Date('Fecha firma contrato:')

    importe_ganador = fields.Float('Importe Ganador:', compute="b_ganador")
    iva = fields.Float('I.V.A', default=0.16)

    # CALCULO DEL IVA
    @api.one
    @api.depends('iva')
    def fallo_iva(self):
        self.total_contratado = (self.iva * self.importe_ganador) + self.importe_ganador

    total_contratado = fields.Float('Total Contratado:	', compute="fallo_iva")

    # RELACION PARA EL DOMAIN DEL ANEXO TECNICO DEL RECURSO DE LA LICITACION
    relacion_concepto_ofi = fields.Text(related="numerolicitacion.programar_obra_licitacion.recursos.concepto.descripcion") #
    # SELECCION DEL RECURSO PARA LA LICITACION
    recursos = fields.Many2many('autorizacion_obra.anexo_tecnico', string="Seleccione un oficio de autorización",
                                )


# TABLA DE PROPUESTA DEL LICITANTE
class PropuestaLic(models.Model):
    _name = 'proceso.propuesta_lic'

    licitacion_id = fields.Many2one('proceso.licitacion')
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')
    monto_partida = fields.Float(string="" )


class Participante(models.Model):
    _name = 'proceso.participante'

    licitacion_id = fields.Char(compute="nombre", store=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    contratista_participantes = fields.Many2many('contratista.contratista')

    @api.one
    def nombre(self):
        self.licitacion_id = self.id


class EstadoObraDesierta(models.Model):
    _name = 'proceso.estado_obra_desierta'
    _rec_name = 'estado_obra_desierta'

    obra_id_desierta = fields.Char(compute="estadoObra", store=True)
    licitacion_id = fields.Char(compute="nombre", store=True)
    estado_obra_desierta = fields.Char(string="estado obra", default="Desierta", readonly=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    fecha_desierta = fields.Date(string="Fecha de Desierta:")
    observaciones_desierta = fields.Text(string="Observaciones:")

    @api.one
    def estadoObra(self):
        self.obra_id_desierta = self.estado_obra_desierta

    @api.one
    def nombre(self):
        self.licitacion_id = self.id


class EstadoObraCancelar(models.Model):
    _name = 'proceso.estado_obra_cancelar'

    obra_id_cancelar = fields.Char(compute="estadoObra", store=True)
    licitacion_id = fields.Char(compute="nombre", store=True)
    estado_obra_cancelar = fields.Char(string="estado obra", default="Cancelada", readonly=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    fecha_cancelado = fields.Date(string="Fecha de Cancelacion:")
    observaciones_cancelado = fields.Text(string="Observaciones:")

    @api.one
    def estadoObraCancelar(self):
        self.obra_id_cancelar = self.estado_obra_cancelar

    @api.one
    def nombre(self):
        self.licitacion_id = self.id



