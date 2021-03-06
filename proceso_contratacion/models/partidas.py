from odoo import models, fields, api, exceptions

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


# CLASE AUXILIAR DE PARTIDAS LICITACION
class PartidasLicitacion(models.Model):
    _name = 'partidas.licitacion'

    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')
    obra = fields.Many2one('registro.programarobra', related="recursos.concepto")
    programaInversion = fields.Many2one('generales.programas_inversion')
    monto_partida = fields.Float(string="Monto", required=True)
    iva_partida = fields.Float(string="Iva", compute="iva")
    total_partida = fields.Float(string="Total", compute="sumaPartidas")
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    @api.depends('monto_partida')
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # METODO CALCULAR TOTAL PARTIDA
    @api.one
    @api.depends('monto_partida')
    def sumaPartidas(self):
        for rec in self:
            rec.update({
                'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida
            })

    # CALCULAR EL IVA TOTAL
    @api.one
    @api.depends('monto_partida')
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })


# CLASE AUXILIAR DE PARTIDAS ADJUDICACION
class PartidasAdjudicacion(models.Model):
    _name = 'partidas.adjudicacion'

    id_sideop_adjudicacion = fields.Integer('ID SIDEOP')
    id_sideop_partida = fields.Integer('ID SIDEOP part')

    obra = fields.Many2one('registro.programarobra', required=True)
    programaInversion = fields.Many2one('generales.programas_inversion')
    monto_partida = fields.Float(string="Monto", required=True)
    iva_partida = fields.Float(string="Iva", compute="iva")
    total_partida = fields.Float(string="Total", compute="sumaPartidas")
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    @api.depends('monto_partida')
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # METODO CALCULAR TOTAL PARTIDA
    @api.one
    @api.depends('monto_partida')
    def sumaPartidas(self):
        for rec in self:
            rec.update({
                'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida
            })

    # CALCULAR EL IVA TOTAL
    @api.one
    @api.depends('monto_partida')
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })


# CLASE DE LAS PARTIDAS Y CONCEPTOS CONTRATADOS
class Partidas(models.Model):
    _name = 'partidas.partidas'
    _rec_name = "numero_contrato"

    # IMPORTACION
    id_partida = fields.Integer('ID PARTIDA')
    id_contrato_sideop = fields.Char(string="num_contrato SIDEOP", required=False, )
    # numero_contrato
    num_contrato_related = fields.Char(string="RELACION A ID CONTRATO", related="numero_contrato.num_contrato_sideop")
    id_contratista = fields.Char('ID CONTRATISTA SIDEOP')
    id_contrato_relacion = fields.Char(string="ESTA ES LA ID DEL CONTRATO A LA PARTIDA PARA LA RELACION")
    # TERMINA IMPORTACION

    numero_contrato = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Numero de Contrato"
                                      , compute="contrato_metodo")  # compute="nombrePartida"

    # OBRA A LA QUE PERTENECE LA PARTIDA
    obra = fields.Many2one('registro.programarobra', )
    # PROGRAMA DE INVERSION
    programaInversion = fields.Many2one('generales.programas_inversion', string="Programa de Inversión",)

    @api.one
    @api.depends('id_contrato_relacion')
    def contrato_metodo(self):
        b_id_ad = self.env['proceso.elaboracion_contrato'].search([('id_ad', '=', self.id_contrato_relacion)], limit=1)
        b_id_lic = self.env['proceso.elaboracion_contrato'].search([('id_lic', '=', self.id_contrato_relacion)], limit=1)
        if b_id_lic.id_lic >= 1:
            self.numero_contrato = b_id_lic.id
        elif b_id_ad.id_ad >= 1:
            self.numero_contrato = b_id_ad.id
        else:
            print('no')

    # RECURSOS LICITACION
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')

    # EL OBJETO ES LA DESCRIPCION DE LA OBRA EN EL CONTRATO
    objeto = fields.Text(string="Objeto", related="numero_contrato.name")

    monto_partida = fields.Float(string="Monto", )
    iva_partida = fields.Float(string="Iva", compute="iva", store=True)
    total_partida = fields.Float(string="Total", compute="SumaContrato", store=True)
    # SUMA DE LAS PARTIDAS
    total_contrato = fields.Float(related="numero_contrato.impcontra")

    # CONCEPTOS CONTRATADOS DE PARTIDAS
    _url_conceptos = fields.Char(compute="_calc_url_conceptos")

    @api.one
    def _calc_url_conceptos(self):
        original_url = "http://35.238.206.12:56733/?id=" + str(self.id) + "&partida=" + str(self.num_contrato_related)
        self._url_conceptos = original_url

    @api.multi
    def imprimir_accion_concepto(self):
        return {"type": "ir.actions.act_url", "url": self._url_conceptos, "target": "new", }

    conceptos_partidas = fields.Many2many('proceso.conceptos_part', required=True)

    conceptos_modificados = fields.Many2many('proceso.conceptos_modificados', required=True)
    justificacion = fields.Text('Justificación de Modificación')
    select_tipo = [('1', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:")

    name = fields.Many2one('proceso.elaboracion_contrato', readonly=True)

    # TOTAL DE LA PARTIDA MONTO CONTRATADO SIN IVA, ESTE USA SIDEOP
    monto_sin_iva = fields.Float(string="Total:", compute="SumaContrato")
    # total con convenio
    monto_sin_iva_modi = fields.Float(string="Total Modificado", compute="nuevo_total_partida")
    # TOTAL DE LA PARTIDA
    total = fields.Float(string="Monto Total Contratado:", compute="totalContrato")

    # METODO PARA ASIGNAR EL TOTAL DEL CONTRATO
    @api.one
    def totalContrato(self):
        _search_cove = self.env['proceso.convenios_modificado'].search_count([("contrato.id", "=", self.id)])
        if _search_cove == 0:
            self.total = self.monto_sin_iva
        else:
            self.total = self.monto_sin_iva_modi

    # BUSQUEDA DE CONVENIOS PARA ESTA PARTIDA
    # FIELD CON EL TOTAL DEL CONVENIO INCLUYE LA SUMA Y RESTA
    convenios_ = fields.Float(string="",  compute="b_convenios" )

    # METODO PARA BUSCAR SI HAY CONVENIO CON REDUCCION O AMPLIACION
    @api.one
    def b_convenios(self):
        _search_cove = self.env['proceso.convenios_modificado'].search([("contrato.id", "=", self.id)])
        acum = 0
        acum2 = 0
        for i in _search_cove:
            if i.tipo_monto == 'AM':
                acum = acum + i.monto_total
            elif i.tipo_monto == 'RE':
                acum2 = acum2 + i.monto_total
            ampliacion = acum
            reduccion = acum2
            total = ampliacion - reduccion
            self.convenios_ = total

    # APLICA EL CALCULO DEL CONVENIO AL MONTO DEL CONTRATO DE LA PARTIDA SI ES QUE EXISTE UNO
    @api.one
    @api.depends('convenios_')
    def nuevo_total_partida(self):
        _search_cove = self.env['proceso.convenios_modificado'].search_count([("contrato.id", "=", self.id)])
        if _search_cove == 0:
            self.monto_sin_iva_modi = 0
        else:
            self.monto_sin_iva_modi = self.monto_sin_iva + self.convenios_

    total_catalogo = fields.Float(string="Monto Total del Catálogo", compute="SumaImporte", required=True)

    diferencia = fields.Float(string="Diferencia:", compute="Diferencia")

    # DEDUCCIONES
    deducciones = fields.Many2many('generales.deducciones', string="Deducciones:")

    # ANTICIPOS
    fecha_anticipos = fields.Date(string="Fecha Anticipo", )
    porcentaje_anticipo = fields.Float(string="Anticipo Inicio", compute="b_anticipo")
    anticipo_material = fields.Float(string="Anticipo Material", compute="b_anticipo")

    # BUSCAR LOS PORCENTAJES DEL ANTICIPO DESDE LA ADJUDICACION O LICITACION RESPECTIVAMENTE
    @api.one
    def b_anticipo(self):
        b_contrato = self.env['proceso.elaboracion_contrato'].search([('id', '=', self.numero_contrato.id)])
        if b_contrato.tipo_contrato == '2':
            self.porcentaje_anticipo = b_contrato.adjudicacion.anticipoinicio
            self.anticipo_material = b_contrato.adjudicacion.anticipomaterial
        elif b_contrato.tipo_contrato == '1':
            self.porcentaje_anticipo = b_contrato.obra.anticipoinicio
            self.anticipo_material = b_contrato.obra.anticipomaterial

    total_anticipo_porcentaje = fields.Float(string="Total Anticipo", compute="anticipo_por")
    importe = fields.Float(string="Importe Contratado")
    anticipo_a = fields.Integer(string="Anticipo", compute="anticipo_inicio")
    iva_anticipo = fields.Float(string="I.V.A", compute="anticipo_iva")
    total_anticipo = fields.Float(string="Total Anticipo", compute="anticipo_total")
    numero_fianza = fields.Char(string="# Fianza", )
    afianzadora = fields.Char(string="Afianzadora", )
    fecha_fianza = fields.Date(string="Fecha Fianza", )
    anticipada = fields.Boolean(string="Anticipada", compute="anticipada_Sel")

    # ESTIMACIONES
    radio_estimacion = [('1', "Estimacion"), ('2', "Escalatoria")]
    tipo_estimacion = fields.Selection(radio_estimacion, string="")
    numero_estimacion = fields.Integer(string="Número de Estimación:", required=False, )
    fecha_inicio_estimacion = fields.Date(string="Del:", required=False, )
    fecha_termino_estimacion = fields.Date(string="Al:", required=False, )
    fecha_presentacion = fields.Date(string="Fecha de presentación:", required=False, )
    fecha_revision = fields.Date(string="Fecha revisión Residente:", required=False, )
    radio_aplica = [('1', "Estimación Finiquito"), ('2', "Amortizar Total Anticipo	")]
    si_aplica = fields.Selection(radio_aplica, string="")
    notas = fields.Text(string="Notas:", required=False, )
    # CALCULADOS DE ESTIMACIONES
    estimado = fields.Float(string="Importe ejecutado estimación:", required=False, )
    amort_anticipo = fields.Float(string="Amortización de Anticipo 30%:", required=False, )
    estimacion_subtotal = fields.Float(string="Neto Estimación sin IVA:", required=False, )
    estimacion_iva = fields.Float(string="I.V.A. 16%", required=False, )
    estimacion_facturado = fields.Float(string="Neto Estimación con IVA:", required=False, )
    estimado_deducciones = fields.Float(string="Menos Suma Deducciones:", required=False, )
    ret_dev = fields.Float(string="Retención/Devolución:", required=False, )
    sancion = fields.Float(string="Sanción por Incump. de plazo:", required=False, )
    a_pagar = fields.Float(string="Importe liquido:", required=False, )
    # porcentaje de la estimacion estimado
    porcentaje_est = fields.Float('% Programado', compute='por_programado')

    @api.one
    def por_programado(self):
        b_esti = self.env['control.estimaciones'].search([('obra.id', '=', self.id)])
        for i in b_esti:
            self.porcentaje_est = i.porcentaje_est

    # PENAS CONVENCIONALES
    menos_clau_retraso = fields.Float(string="Menos Clausula Retraso:", required=False, )
    sancion_incump_plazo = fields.Integer(string="Sanción por Incump. de plazo:", required=False, )

    # CONVENIOS MODIFICATORIOS
    convenios_modificatorios = fields.Many2many('proceso.convenios', string="Conv. Modificatorios")
    # RESIDENCIA
    residente_obra = fields.Many2one(comodel_name='res.users',string='Residente obra:')
    supervision_externa = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:")
    director_obras = fields.Char('Director de obras:')
    puesto_director_obras = fields.Text('Puesto director de obras:')
    # Supervicion de obra (JFernandez)
    ruta_critica = fields.Many2many('proceso.rc')
    total_ = fields.Integer(compute='suma_importe')
    # Contador de convenios por obra
    count_convenios_modif = fields.Integer(compute="contar_covenios")
    # VISTA DE INFORMACION DE LA PARTIDA
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="obra.obra_planeada.ejercicio")
    municipio = fields.Many2one('generales.municipios', 'Municipio', related="obra.obra_planeada.municipio")
    estado = fields.Many2one('generales.estado', 'Municipio', related="obra.obra_planeada.estado")
    localidad = fields.Text(string="Localidad", readonly="True", related="obra.obra_planeada.localidad")
    # localidad = fields.Text(string="Localidad", readonly="True", related="obra.obra_planeada.localidad")
    fecha = fields.Date(string="Fecha", related="numero_contrato.fecha")
    fechainicio = fields.Date(string="Fecha de Inicio", related="numero_contrato.fechainicio")
    fechatermino = fields.Date(string="Fecha de Termino", related="numero_contrato.fechatermino")
    supervisionexterna1 = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:",
                                          related="numero_contrato.supervisionexterna1")
    # RELACION CONTRATISTA
    contratista = fields.Many2one('contratista.contratista', related="numero_contrato.contratista")

    # NOMBRE DE LA PARTIDA = AL DEL CONTRATO
    nombre_partida = fields.Char(string="nombre partida", required=False, )
    # PENDIENTE
    nueva_partida = fields.Char(string="nombre partida", required=False, )

    # A.FIS A.FIN
    a_fis = fields.Float(string="A.FIS", default=0.0, required=False, )
    a_fin = fields.Float(string="A.FIN", default=0.0, required=False, )

    # INICIO FINIQUITO #
    fecha1 = fields.Date(string="Fecha de aviso de terminación de los trabajos")
    fecha2 = fields.Datetime(string="Fecha y hora verificación de la terminación de los trabajos")
    numero = fields.Char(string="Número bitácora del contrato")
    nota1 = fields.Text(string="Nota de bitácora aviso terminación")
    fecha3 = fields.Date(string="Fecha nota bitácora")
    fecha4 = fields.Date(string="Fecha de aviso de terminación de trabajos")
    fecha5 = fields.Date(string="Fecha de inicio Real del contrato")
    fecha6 = fields.Date(string="Fecha de termino real del contrato")
    fecha7 = fields.Datetime(string="Fecha y hora programada del acta de recepción de los trabajos")
    fecha8 = fields.Datetime(string="Fecha y hora entrega de la obra")
    fecha9 = fields.Datetime(string="Fecha y hora finiquito")
    fecha10 = fields.Datetime(string="Fecha y hora acta cierre administrativo")
    fecha11 = fields.Datetime(string="Fecha y hora acta de extinción de derechos")
    description = fields.Text(string="Descripción de los trabajos")
    creditosContra = fields.Char(string="Créditos en contra del contratista al finalizar la obra")
    # FIN FINIQUITO #
    # ID PARTIDA
    p_id = fields.Integer('ID DE LA PARTIDA')
    # RESTRICCION DEL PROGRAMA, SI NO HAY PROGRAMA NO PERMITE REGISTRAR UNA ESTIMACION
    verif_programa = fields.Boolean(string="", compute="programa_verif")
    # VALOR DEL IVA TRAIDO DESDE CONFIGURACION
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")
    # CONTAR REGISTROS DE ESTIMACIONES
    contar_estimaciones = fields.Integer(compute='ContarEstimaciones', string="PRUEBA")
    # M2M PARA PODER HACER REPORTE DE ESTADO DE CUENTA DE ESTIMACIONES MAS SU METODO
    esti = fields.Many2many(comodel_name="control.estimaciones", nolabel="1", compute="estimaciones_report")
    # CONTROL DE EXPEDIENTES
    tabla_control = fields.One2many('control.expediente', 'p_id')

    # GALERIA DE IMAGENES DE AVANCE FINANCIERO
    galleria = fields.Many2many('avance.avance_fisico', nolabel=True)

    # ESTIMACION ENLACE
    estimacion_id = fields.Char(compute="nombre", store=True)
    _url = fields.Char(compute="_calc_url")

    # SEMAFORO
    estado_obra = fields.Many2many('semaforo.estado_obra')
    estado_actividad = fields.Many2many('semaforo.actividad')
    recursos_semaforo = fields.Many2many(comodel_name="proceso.anexos", related="numero_contrato.anexos")
    convenio_semaforo = fields.Many2many(comodel_name="proceso.convenios_modificado", compute="semaforo_convenios")
    avance_semaforo = fields.Many2many(comodel_name="proceso.iavance", compute="semaforo_avance")

    @api.multi
    def semaforo_avance(self):
        partidas = self.env['partidas.partidas']
        _search_partida = self.env['partidas.partidas'].search(
            [("id", "=", self.id)]).id

        avanc = self.env['proceso.iavance'].search(
            [("numero_contrato.id", "=", self.id)])

        for i in avanc:
            datos_avance = {
                'avance_semaforo': [[1, i.id, {
                    'fecha_actual': i.fecha_actual,
                    'situacion_contrato': i.situacion_contrato,
                    'porcentaje_estimado': i.porcentaje_estimado,
                    'com_avance_obra': i.com_avance_obra,
                    'comentarios_generales': i.comentarios_generales,
                }]]}
            partida_est = partidas.browse(_search_partida)
            avance_semaforo = partida_est.update(datos_avance)

    @api.multi
    def semaforo_convenios(self):
        partidas = self.env['partidas.partidas']
        _search_partida = self.env['partidas.partidas'].search(
            [("id", "=", self.id)]).id

        conv = self.env['proceso.convenios_modificado'].search(
            [("contrato.id", "=", self.id)])

        for i in conv:
            datos_conv = {
                'convenio_semaforo': [[1, i.id, {
                    'fecha_convenios': i.fecha_convenios,
                    'referencia': i.referencia,
                    'observaciones': i.observaciones,
                    'monto_total': i.monto_total,
                    'plazo_fecha_inicio': i.plazo_fecha_inicio,
                    'plazo_fecha_termino': i.plazo_fecha_termino,
                    'objeto_nuevo_objeto': i.objeto_nuevo_objeto,
                }]]}
            partida_est = partidas.browse(_search_partida)
            convenio_semaforo = partida_est.update(datos_conv)

    @api.one
    def _calc_url(self):
        original_url = "http://sidur.galartec.com:56733/galeria/?id=" + str(self.id)
        self._url = original_url

    @api.multi
    def imprimir_accion(self):
        return {"type": "ir.actions.act_url", "url": self._url, "target": "new", }

    # METODO PARA CREAR NUEVO DOCUMENTO CON BOTON
    @api.multi
    def expediente_crear(self):
        # VISTA OBJETIVO
        view = self.env.ref('control_expediente.form_control_expediente')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Control Expediente',
            'res_model': 'control.expediente',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_p_id': self.id},
            'view_id': view.id,
        }

    # ACTIVADOR DE ONCHANGE PARA PRUEBAS
    prueba_expediente = fields.Char(string="PRUEBA METODO EJECUCION", required=False, )

    # METODO PARA INSERTAR EXPEDIENTES A LA TABLA
    @api.multi  # if these fields are changed, call method
    @api.onchange('p_id', 'prueba_expediente')
    def control_expediente(self):
        b_expediente = self.env['control_expediente.control_expediente'].search([])
        b_partida = self.env['partidas.partidas'].search([('id', '=', self._origin.id)])

        self.update({
            'tabla_control': [[5]]
        })

        for c_exp in b_expediente:
            self.update({
                'tabla_control': [[0, 0, {'nombre': c_exp.id,
                                          'p_id': self.id,
                                        'etapa': c_exp.etapa}]]
            })

    @api.multi
    def estimaciones_report(self):
        partidas = self.env['partidas.partidas']
        _search_partida = self.env['partidas.partidas'].search(
            [("id", "=", self.id)]).id
        dedu = self.env['control.estimaciones'].search(
            [("obra.id", "=", self.id)])
        for i in dedu:
            datos_esti = {
                'esti': [[1, i.id, {
                    'idobra': i.idobra,
                    'tipo_estimacion': i.tipo_estimacion,
                    'fecha_inicio_estimacion': i.fecha_inicio_estimacion,
                    'fecha_termino_estimacion': i.fecha_termino_estimacion,
                    'amort_anticipo': i.amort_anticipo,
                    'estimado': i.estimado,
                    'a_pagar': i.a_pagar,
                }]]}
            partida_est = partidas.browse(_search_partida)
            esti = partida_est.update(datos_esti)

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def ContarEstimaciones(self):
        print('SE CONTO LA ESTIMACION C:')
        count = self.env['control.estimaciones'].search_count([('obra', '=', self.id)])
        self.contar_estimaciones = count

    @api.multi
    def CategoriasForm(self):
        view = self.env.ref('proceso_contratacion.categoria_seccion_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Categorias',
            'res_model': 'catalogo.categoria',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
        }

    @api.multi
    def write(self, values):
        if self.fecha_anticipos and self.fecha_fianza and self.afianzadora and self.numero_fianza and \
                self.anticipo_material:
            return super(Partidas, self).write(values)
        elif self.ruta_critica is not False:
            return super(Partidas, self).write(values)
        elif self.conceptos_partidas:
            version = self.env['proceso.conceptos_modificados']
            id_partida = self.id
            datos = {'justificacion': values['justificacion'], 'obra': id_partida, 'tipo': values['tipo']}
            nueva_version = version.create(datos)
            values['tipo'] = ""
            values['justificacion'] = ""
            return super(Partidas, self).write(values)
        else:
            return super(Partidas, self).write(values)

    programa_id = fields.Many2one('programa.programa_obra', string="ID DE LA VENTANA DEL PROGRAMA PARA ESTA PARTIDA", compute="programas")

    # METODO PARA INGRESAR A RECURSOS BOTON
    @api.multi
    def programas(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.vista_form_programa')
        # CONTADOR SI YA FUE CREADO
        count = self.env['programa.programa_obra'].search_count([('obra.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['programa.programa_obra'].search([('obra.id', '=', self.id)])
        if count == 0:
            self.programa_id = []
        else:
            self.programa_id = search[0].id
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search[0].id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }

    @api.one
    def FechaAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.fecha_anticipos = search.fecha_anticipos

    @api.one
    def PorcentajeAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.porcentaje_anticipo = search.porcentaje_anticipo

    @api.one
    def TotalAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.total_anticipo = search.total_anticipo

    # METODO PARA ABRIR ANTICIPOS CON BOTON
    @api.multi
    def anticipoBoton(self):
        view = self.env.ref('proceso_contratacion.partidas_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'anticipos',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # METODO PARA VERIFICAR SI HAY PROGRAMAS
    @api.one
    def programa_verif(self):
        busqueda = self.env['programa.programa_obra'].search([('obra.id', '=', self.id)])
        busqueda2 = self.env['programa.programa_obra'].search_count([('obra.id', '=', self.id)])
        print(busqueda2)
        if busqueda2 >= 1:
            print("SI HAY PROGRAMA")
            self.verif_programa = True
        else:
            print("NO HAY PROGRAMA")
            self.verif_programa = False

    # METODO PARA VERIFICAR SI YA SE ANTICIPO UNA PARTIDA
    @api.one
    def anticipada_Sel(self):
        if self.fecha_anticipos and self.numero_fianza and self.afianzadora and self.fecha_fianza:
            self.anticipada = True
        else:
            self.anticipada = False

    # METODO PARA VERIFICAR SI HAY ANTICIPO
    @api.multi
    def VerifAnti(self, vals):
        if self.fecha_anticipos and self.fecha_fianza and self.afianzadora and self.numero_fianza and self.anticipo_material is not False:
            self.anticipada = True
        else:
            self.anticipada = False

    # METODO PARA CALCULAR EL PORCENTAJE DEL ANTICIPO
    @api.one
    @api.depends('porcentaje_anticipo')
    def anticipo_por(self):
        for rec in self:
            rec.update({
                'total_anticipo_porcentaje': rec.porcentaje_anticipo
            })

    # METODO PARA CALCULAR EL ANTICIPO DE INICIO
    @api.one
    @api.depends('total_partida', 'porcentaje_anticipo')
    def anticipo_inicio(self):
        for rec in self:
            rec.update({
                'anticipo_a': rec.monto_sin_iva * rec.total_anticipo_porcentaje
            })

    # MEOTODO PARA CALCULAR IVA DE ANTICIPO ---VER CUESTION DEL IVA
    @api.one
    @api.depends('anticipo_a')
    def anticipo_iva(self):
        for rec in self:
            rec.update({
                'iva_anticipo': rec.anticipo_a * self.b_iva
            })

    # METODO PARA CALCULAR EL TOTAL DEL ANTICIPO
    @api.one
    @api.depends('anticipo_a', 'iva_anticipo')
    def anticipo_total(self):
        for rec in self:
            rec.update({
                'total_anticipo': rec.anticipo_a + rec.iva_anticipo
            })

    # METODO PARA INSERTAR EL NUMERO DEL CONTRATO DENTRO DE LA PARTIDA PARA HACER CONEXION
    '''@api.one
    def nombrePartida(self):
        self.numero_contrato = self.enlace.id'''

    # METODO DE JCHAIRZ
    @api.onchange('ruta_critica')
    def suma_importe(self):
        suma = 0
        for i in self.ruta_critica:
            resultado = i.porcentaje_est
            suma += resultado
            self.total_ = suma

    # JCHAIREZ
    @api.onchange('total_')
    def validar_total_importe(self):
        if self.total_ > 100:
            raise ValidationError("Ups! el porcentaje no puede ser mayor a 100 %")

    # Jesus Fernandez metodo para abrir ruta critica
    @api.multi
    def ruta_critica_over(self):
        view = self.env.ref('ejecucion_obra.proceso_rutac_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ruta critica',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    # JFernandez metodo para contar el numero de convenios que tiene cada obra
    @api.one
    def contar_covenios(self):
        count = self.env['proceso.convenios_modificado'].search_count([('contrato.id', '=', self.id)])
        self.count_convenios_modif = count

    # METODO CALCULAR DIFERENCIA ENTRE PARTIDA Y CONCEPTOS
    @api.one
    def Diferencia(self):
        _search_cove = self.env['proceso.convenios_modificado'].search_count([("contrato.id", "=", self.id)])
        for rec in self:
            if _search_cove == 0:
                rec.update({
                    'diferencia': self.total_catalogo - self.monto_sin_iva
                })
            else:
                rec.update({
                    'diferencia': self.total_catalogo - self.monto_sin_iva_modi
                })

    # METODO CALCULAR TOTAL PARTIDA UNICA
    @api.one
    @api.depends('monto_partida')
    def SumaContrato(self):
        for rec in self:
            rec.update({
                'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida,
                'monto_sin_iva': rec.monto_partida
            })

    # CALCULAR EL IVA TOTAL
    @api.one
    @api.depends('monto_partida')
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })

    # METODO PARA SUMAR LOS IMPORTES DE LOS CONCEPTOS
    @api.one
    @api.depends('conceptos_partidas')
    def SumaImporte(self):
        suma = 0
        for i in self.conceptos_partidas:
            resultado = i.importe
            suma = suma + resultado
            self.total_catalogo = suma

    # METODO DE ENLACE A ESTIMACIONES
    @api.one
    def nombre(self):
        self.estimacion_id = self.obra


class ConveniosM(models.Model):
    _name = 'proceso.convenios'

    fecha_convenios = fields.Date("Fecha:")
    referencia_convenios = fields.Char("Referencia:")
    observaciones_convenios = fields.Char("Observaciones:")
    tipo_convenio = fields.Char("Tipo de Convenio:", default="Escalatorio", readonly="True")
    importe_convenios = fields.Float('Importe:')
    iva_convenios = fields.Float('I.V.A:')
    total_convenios = fields.Float('Total:')


# CONTENIDO DE LA TABLA DE PROGRAMA DE OBRA
class ProgramaContrato(models.Model):
    _name = 'proceso.programa'

    obra = fields.Many2one('partidas.partidas', string='Obra:')
    # IMPORTACION
    id_prog = fields.Integer(string="ID PROGRAMA", required=False, )
    # TERMINA IMPORTACION

    fecha_inicio = fields.Date('Fecha Inicio:', default=fields.Date.today(), required=True)
    fecha_termino = fields.Date('Fecha Término:', required=True)
    monto = fields.Float('Monto:', required=True)

    # METODO para verificar fechas de programa
    @api.multi
    @api.onchange('fecha_termino')
    def validar_fecha_programa(self):
        if str(self.fecha_termino) < str(self.fecha_inicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la fecha de inicio, '
                                     'por favor seleccione una fecha posterior')
        else:
            return False


