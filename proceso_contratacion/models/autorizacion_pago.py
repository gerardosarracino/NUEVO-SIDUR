from odoo import api, fields, models


class AutorizacionPago(models.Model):
    _name = "estimacion.autorizacion_pago"
    _rec_name = 'numero_factura'

    vinculo_estimaciones = fields.Many2one('control.estimaciones', string='Estimación id')  # ID DE ESTIMACION
    numero_contrato = fields.Many2one('partidas.partidas', string='Contrato', store=True)  # NUMERO DE CONTRATO DE PARTIDA

    fecha_factura = fields.Date('Fecha de Factura')

    @api.multi
    @api.onchange('vinculo_estimaciones')
    def _numero_contrato(self):
        if not self.vinculo_estimaciones:
            pass
        else:
            self.numero_contrato = self.vinculo_estimaciones.obra.id
            self.programa_inversion = self.vinculo_estimaciones.obra.programaInversion
            self.contratista_contrato = self.vinculo_estimaciones.obra.contratista.id
            self.estimado = self.vinculo_estimaciones.estimado
            self.amort_anticipo = self.vinculo_estimaciones.amort_anticipo
            self.estimacion_subtotal = self.vinculo_estimaciones.estimacion_subtotal
            self.estimacion_iva = self.vinculo_estimaciones.estimacion_iva
            self.estimacion_facturado = self.vinculo_estimaciones.estimacion_facturado
            self.estimado_deducciones = self.vinculo_estimaciones.estimado_deducciones
            self.sancion = self.vinculo_estimaciones.sancion
            self.ret_neta_est = self.vinculo_estimaciones.ret_neta_est
            self.a_pagar = self.vinculo_estimaciones.a_pagar

    autorizacion_pago = fields.Char(string='Autorizacion de Pago No.', required=True, store=True)
    programa_inversion = fields.Many2one('generales.programas_inversion', required=True, string='Fondo')

    fecha = fields.Date(string='Fecha de autorizacion', required=True)

    contratista_contrato = fields.Many2one('contratista.contratista', store=True)
    obra = fields.Many2one(string='Obra:', readonly=True, related="numero_contrato.obra")  # OBRA DE LA PARTIDA

    numero_factura = fields.Char(string='Numero de Factura', required=True, size=10)

    # CAMPOS ESTIMADOS

    estimado = fields.Float(string="Importe ejecutado estimación:", store=True, digits=(12, 2))
    amort_anticipo = fields.Float(string="Amortización de Anticipo:", compute="amortizacion_anticipo", store=True, digits=(12, 2))
    estimacion_subtotal = fields.Float(string="Neto Estimación sin IVA:", store=True, digits=(12, 2))
    estimacion_iva = fields.Float(string="I.V.A. 16%", store=True, digits=(12, 2))
    estimacion_facturado = fields.Float(string="Neto Estimación con IVA:", store=True, digits=(12, 2))
    estimado_deducciones = fields.Float(string="Menos Suma Deducciones:", store=True, digits=(12, 2))
    sancion = fields.Float(string="Sanción por Incump. de plazo:", digits=(12, 2),store=True)
    ret_neta_est = fields.Float(string='', store=True, digits=(12, 2))
    a_pagar = fields.Float(string="Importe liquido:", store=True, digits=(12, 2))

    inversion_anual_aut = fields.Float('Inversion anual autorizada', digits=(12, 2))
    inversion_ejercida = fields.Float('Inversion ejercida', digits=(12, 2))
    saldo_por_ejercer = fields.Float('Saldo por ejercer', digits=(12, 2))
    creditos_deudores = fields.Float('Creditos deudores', digits=(12, 2))


    '''@api.onchange('autorizacion_pago') PARA DESPUES TALVEZ
    def actualizar_autorizacion(self):
        if not self.autorizacion_pago:
            pass
        else:
            b_est = self.env['control.estimaciones'].browse(self.vinculo_estimaciones.id)
            dato = {
                'con_autorizacion': True
            }
            listax = b_est.write(dato)'''

    # AGREGAR PAGO FINIQUITO
    radio_pago = [(
        'Estimacion', "Estimacion"), ('Pago', "Pago de Anticipo")]
    tipo_pago = fields.Selection(radio_pago, string="Tipo de Pago")

