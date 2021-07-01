from odoo import models, fields, api, exceptions
from datetime import datetime
import calendar
import datetime


class OrdenesCambio(models.Model):
    _name = 'ordenes.ordenes_cambio'
    _rec_name = 'id_partida'

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    numero_contrato = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Numero de Contrato", related="id_partida.numero_contrato")
    contratista = fields.Many2one('contratista.contratista', related="id_partida.contratista")
    obra = fields.Many2one('registro.programarobra', related="id_partida.obra")
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="id_partida.ejercicio")
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo", related="id_partida.obra.obra_planeada.tipoObra")

    # ordenes_conceptos_espejo = fields.Many2many('ordenes.conceptos_espejo', store=True)  # ORDENES DE CAMBIO CONCEPTOS EN ESPEJO
    ordenes_conceptos_espejo = fields.Many2many('proceso.conceptos_part', related="id_partida.conceptos_partidas")  # ORDENES DE CAMBIO CONCEPTOS EN ESPEJO
    ordenes_conceptos_related = fields.Many2many('ordenes.conceptos_cambio', )

    total_contratado = fields.Float('Total Contratado', related="id_partida.total")
    total_catalogo = fields.Float('Total Catalogo', related="id_partida.total_catalogo")
    diferencia = fields.Float('Diferencia', related="id_partida.diferencia")

    subtotal_ordenes = fields.Float('Subtotal de ordenes')

    '''@api.multi
    @api.onchange('id_partida')
    def conceptos_espejo(self):
        b_conceptos = self.env['partidas.partidas'].search(
            [('id', '=', self.id_partida.id)])

        self.update({
            'ordenes_conceptos_espejo': [[5]]
        })

        for y in b_conceptos.conceptos_partidas:
            self.update({
                'ordenes_conceptos_espejo': [
                    [0, 0, {'id_partida': self.id_partida, 'categoria': y.categoria,
                            'related_categoria_padre': y.related_categoria_padre,
                            'clave_linea': y.clave_linea, 'concepto': y.concepto,
                            'medida': y.medida,
                            'importe': y.importe,
                            'precio_unitario': y.precio_unitario,
                            'cantidad': y.cantidad}]]
            })'''

    @api.multi
    def OrdenesLista(self):
        # VISTA OBJETIVO
        form = self.env.ref('ordenes_cambio.ordenes_cambio_conceptos_form')
        # tree = self.env.ref('ordenes_cambio.ordenes_cambio_lista_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes de Cambio',
            'res_model': 'ordenes.conceptos_cambio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': False,
            'domain': [('id_partida', '=', self.id_partida.id)],
            'views': [
                (form.id, 'form'),
                # (form.id, 'form'),
            ],
        }


    '''@api.multi
    def unlink(self):
        self.ordenes_conceptos_espejo.unlink()
        return super(OrdenesCambio, self).unlink()'''


class ListaOrdenes(models.Model):
    _name = 'ordenes.lista_ordenes_cambio'
    _rec_name = 'numero_orden'

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    id_orden = fields.Many2one(comodel_name="ordenes.ordenes_cambio", string="id orden", store=True)
    ordenes_conceptos = fields.Many2many('ordenes.conceptos_lista', store=True)
    numero_orden = fields.Integer(store=True)
    comentario_orden = fields.Text('Comentario General de la Orden de Cambio')
    monto_orden = fields.Float('Monto de la Orden de Cambio', store=True)
    aplicado = fields.Boolean(string="Indica si ya fue Aplicado", store=True)

    @api.multi
    @api.onchange('ordenes_conceptos')
    def onchange_monto_orden(self):
        acum = 0
        for i in self.ordenes_conceptos:
            acum += i.importe
            self.monto_orden = acum

    @api.multi
    def AplicarCambios(self):
        datos = {}
        self.aplicado = True
        b_partida = self.env['partidas.partidas'].browse(self.id_partida.id)

        acum_c = 0
        for conceptos in self.ordenes_conceptos:
            acum_c += conceptos.importe

            importe_red = 0
            importe_amp = 0
            if conceptos.importe < 0: # negativo
                importe_red = conceptos.importe
            elif conceptos.importe > 1: # positivo
                importe_amp = conceptos.importe



            monto_contratado = b_partida.total

            b_acumulado_ordenes = self.env['ordenes.conceptos_cambio'].search([('id_partida.id' , '=', self.id_partida.id)])

            acum = 0
            for ac in b_acumulado_ordenes:
                acum += ac.importe

            porcentaje_acumulado = (acum_c + acum) / monto_contratado

            datos = ({
                'ordenes_conceptos': [[0, 0, {'id_partida': self.id_partida.id,
                   'numero_orden_cambio': self.numero_orden,
                   'ampliacion': importe_amp,
                   'reduccion': importe_red,
                   'acumulado': acum + acum_c,
                   'porcentaje_acumulado': porcentaje_acumulado,


                   'categoria': conceptos.categoria.id,
                   'related_categoria_padre': conceptos.related_categoria_padre.id,
                   'clave_linea': conceptos.clave_linea,
                   'concepto': conceptos.concepto,
                   'medida': conceptos.medida,
                   'precio_unitario': conceptos.precio_unitario,
                   'importe': conceptos.importe,
                   'cantidad': conceptos.cantidad}]]
            })
            r = b_partida.write(datos)

    @api.multi
    def unlink(self):
        self.ordenes_conceptos.unlink()
        return super(ListaOrdenes, self).unlink()

    @api.model
    def create(self, values):
        search = self.env['ordenes.lista_ordenes_cambio'].search_count([('id_partida', '=', values['id_partida'])])
        values['numero_orden'] = int(search + 1)
        return super(ListaOrdenes, self).create(values)


class OrdenesConceptos(models.Model):
    _name = 'ordenes.conceptos_cambio'
    _rec_name = 'numero_orden_cambio'

    numero_orden_cambio = fields.Integer('# DE ORDEN', store=True)
    reduccion = fields.Float('Monto de reduccion', store=True)
    ampliacion = fields.Float('Monto de ampliacion', store=True)
    acumulado = fields.Float('Monto acumulado', store=True)
    porcentaje_acumulado = fields.Float('%', store=True, digits=(12,3))
    fecha_supervision = fields.Date(string="Fecha VoBo", required=False, )
    fecha_autorizacion = fields.Date(string="Fecha autorizacion", required=False, )
    # ordenes_conceptos = fields.Many2many('ordenes.conceptos_lista')
    ordenes_conceptos = fields.One2many('ordenes.conceptos_lista', 'id_cambio')

    '''@api.multi
    @api.onchange('ordenes_conceptos')
    def onchange_method(self):
        acum_concepto = 0
        for i in self.ordenes_conceptos:
            acum_concepto += i.importe
        if acum_concepto > 0:
            self.ampliacion = acum_concepto
        elif acum_concepto < 0:
            self.reduccion = acum_concepto

        search_ordenes = self.env['ordenes.conceptos_cambio'].search([('id_partida.id', '=', self.id_partida.id)])
        acum_amp = 0
        acum_re = 0
        for i in search_ordenes:
            acum_amp += i.ampliacion
            acum_re += i.reduccion
            
        self.acumulado = acum_re + acum_amp

        self.porcentaje_acumulado = (self.acumulado / self.id_partida.total) * 100'''

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    id_orden = fields.Many2one(comodel_name="ordenes.ordenes_cambio", string="id orden", store=True)
    completo = fields.Boolean(string="Completo")

    @api.model
    def create(self, values):
        search = self.env['ordenes.conceptos_cambio'].search_count([('id_orden', '=', values['id_orden'])])
        values['numero_orden_cambio'] = int(search + 1)
        print(values['numero_orden_cambio'])
        res = super(OrdenesConceptos, self).create(values)
        datos = {'ordenes_conceptos_related': [[4, res.id, {}]]}
        tt = self.env['ordenes.ordenes_cambio'].browse(values['id_orden'])
        xd = tt.write(datos)
        print(search, '=', values['id_orden'])
        return res

    @api.multi
    def boton_aplicar(self):
        self.completo = False
        b_clave = self.env['proceso.conceptos_part'].search([('clave_linea', '=', self.clave_linea),
                                                             ('id_partida', '=', self.id_partida.id)])
        if b_clave:  # YA EXISTE EL CONCEPTO
            browse_concepto = self.env['proceso.conceptos_part'].browse(b_clave.id)
            precio_unitario = 0
            if float(b_clave.precio_unitario) < 0:
                precio_unitario = float(b_clave.precio_unitario * -1) - self.precio_unitario
            else:
                precio_unitario = float(b_clave.precio_unitario) - self.precio_unitario

            datos = {'id_partida': self.id_partida.id,
                     'categoria': self.categoria.id,
                     'related_categoria_padre': self.related_categoria_padre.id,
                     'clave_linea': self.clave_linea,
                     'concepto': self.concepto,
                     'medida': self.medida,
                     'precio_unitario': precio_unitario,
                     'importe': float(b_clave.importe) - float(self.importe),
                     'cantidad': float(b_clave.cantidad) - float(self.cantidad),
                     }
            r = browse_concepto.write(datos)


    @api.multi
    def boton_no_aplicar(self):
        self.completo = True
        b_clave = self.env['proceso.conceptos_part'].search([('clave_linea', '=', self.clave_linea),
                                                             ('id_partida', '=', self.id_partida.id)])

        precio_unitario = 0
        if float(b_clave.precio_unitario) < 0:
            precio_unitario = float(self.precio_unitario) + float(b_clave.precio_unitario * -1)
        else:
            precio_unitario = float(self.precio_unitario) + float(b_clave.precio_unitario)

        if b_clave:  # YA EXISTE EL selfCONCEPTO
            browse_concepto = self.env['proceso.conceptos_part'].browse(b_clave.id)
            datos = {'id_partida': self.id_partida.id,
                     'categoria': self.categoria.id,
                     'related_categoria_padre': self.related_categoria_padre.id,
                     'clave_linea': self.clave_linea,
                     'concepto': self.concepto,
                     'medida': self.medida,
                     'precio_unitario': precio_unitario,
                     'importe': float(self.importe) + float(b_clave.importe),
                     'cantidad': float(self.cantidad) + float(b_clave.cantidad)
                     }
            r = browse_concepto.write(datos)

    @api.multi
    def AgregarConcepto(self):
        # VISTA OBJETIVO
        form = self.env.ref('ordenes_cambio.form_ventana_conceptos_ordeneslista')
        # tree = self.env.ref('ordenes_cambio.ordenes_cambio_lista_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes de Cambio',
            'res_model': 'ordenes.conceptos_lista',
            'view_mode': 'form',
            'target': 'new',
            'view_id': False,
            'context': {'default_id_partida': self.id_partida.id,
                        'default_id_orden': self.id_orden.id,
                        'default_id_cambio': self.id,
                        },
            'views': [
                (form.id, 'form'),
            ],
        }

    @api.multi
    def borrar(self):
        self.ordenes_conceptos.unlink()
        self.unlink()
        return super(OrdenesConceptos, self).unlink()


class OrdenesConceptosLista(models.Model):
    _name = 'ordenes.conceptos_lista'
    _rec_name = 'clave_linea'

    concepto_partida = fields.Many2one(comodel_name="proceso.conceptos_part", string="Seleccionar Concepto", required=False, )

    @api.onchange('concepto_partida')
    def onchange_concepto(self):
        self.related_categoria_padre = self.concepto_partida.related_categoria_padre.id
        self.categoria = self.concepto_partida.categoria.id
        self.descripcion = self.concepto_partida.descripcion
        self.clave_linea = self.concepto_partida.clave_linea
        self.concepto = self.concepto_partida.concepto
        self.medida = self.concepto_partida.medida
        self.precio_unitario = self.concepto_partida.precio_unitario
        self.cantidad = self.concepto_partida.cantidad
        self.importe = self.concepto_partida.importe

    related_categoria_padre = fields.Many2one('catalogo.categoria', store=True)  # related="categoria.parent_id", store=True
    categoria = fields.Many2one('catalogo.categoria', 'Categoria', store=True)
    descripcion = fields.Text('Descripción',store=True)
    name = fields.Many2one('catalogo.categoria', 'Categoria Padre',store=True)
    clave_linea = fields.Char('Clave',store=True)
    concepto = fields.Text(store=True)
    medida = fields.Char(store=True)
    precio_unitario = fields.Float(store=True)
    cantidad = fields.Float(store=True)
    importe = fields.Float(compute="sumaCantidad", store=True)

    comentario = fields.Text(string="Comentario de Orden de Cambio", required=False, )

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    id_orden = fields.Many2one(comodel_name="ordenes.ordenes_cambio", string="id orden", store=True)
    id_cambio = fields.Many2one(comodel_name="ordenes.conceptos_cambio", string="id orden", store=True)

    @api.model
    def create(self, values):
        res = super(OrdenesConceptosLista, self).create(values)
        datos = {'ordenes_conceptos': [[4, res.id, {}]]}
        tt = self.env['ordenes.conceptos_cambio'].browse(values['id_cambio'])
        oc = tt.update(datos)
        ord = self.env['ordenes.ordenes_cambio'].browse(values['id_orden'])
        search_ordenes = self.env['ordenes.conceptos_cambio'].search([('id_partida', '=', values['id_partida'])])
        acum_amp = 0
        acum_re = 0
        for vals in search_ordenes:
            # acum += vals['acumulado']
            acum_amp += vals['ampliacion']
            acum_re += vals['reduccion']
        acum = acum_amp + acum_re
        reduccion = 0
        ampliacion = 0
        if values['importe'] < 0:  # reduccion
            reduccion = values['importe']
            datos2 = {
                'reduccion': tt.reduccion + reduccion,
                'acumulado': acum + reduccion,
                'porcentaje_acumulado': ((acum + reduccion) / tt.id_partida.total) * 100
            }
            r = tt.write(datos2)
            datos_ord = {'subtotal_ordenes': acum + reduccion,}
            rord = ord.write(datos_ord)
        else:
            ampliacion = values['importe']
            datos2 = {
                'ampliacion': tt.ampliacion + ampliacion,
                'acumulado': acum + ampliacion,
                'porcentaje_acumulado': ((acum + ampliacion) / tt.id_partida.total) * 100
            }
            datos_ord = {'subtotal_ordenes': acum + ampliacion, }
            rord = ord.write(datos_ord)
            r = tt.write(datos2)
        search_concepto = self.env['proceso.conceptos_part'].browse(values['concepto_partida'])
        datos_concepto = {
            'cantidad_ajustada': values['cantidad'],
            'importe_ajustado': values['importe'],
        }
        rc = search_concepto.write(datos_concepto)
        return res

    @api.multi
    def borrar(self):
        tt = self.env['ordenes.conceptos_cambio'].browse(self.id_cambio)
        print(tt)
        reduccion = 0
        ampliacion = 0
        if self.importe < 0:  # reduccion
            reduccion = self.importe
        else:
            ampliacion = self.importe
        datos = {
            'ampliacion': self.id_cambio.ampliacion - ampliacion,
            'reduccion': self.id_cambio.reduccion - reduccion,
            'acumulado': self.id_cambio.acumulado - self.importe,
            'porcentaje_acumulado': ((self.id_cambio.acumulado - self.importe) / self.id_partida.total) * 100
        }
        r = self.id_cambio.write(datos)
        self.unlink()

        return super(OrdenesConceptosLista, self).unlink()

    @api.multi
    @api.onchange('precio_unitario', 'cantidad')
    def sumaCantidad(self):
        for rec in self:
            rec.update({
                'importe': rec.cantidad * rec.precio_unitario
            })





