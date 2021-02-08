# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date
from datetime import datetime
import calendar
import warnings


class EstimacionesBis(models.Model):
    _inherit = 'control.estimaciones'

    # SECCION DE ESTIMACION BIS
    # CALCULO DE LA ESTIMACION
    estimado_bis = fields.Float(string="Importe ejecutado estimación:", store=True, digits=(12, 2))

    amort_anticipo_bis = fields.Float(string="Amortización de Anticipo:", store=True, digits=(12, 2))

    amort_anticipo_partida_bis = fields.Float(store=True)

    estimacion_subtotal_bis = fields.Float(string="Neto Estimación sin IVA:", store=True, digits=(12, 2))

    estimacion_iva_bis = fields.Float(string="I.V.A. 16%", store=True, digits=(12, 2))

    estimacion_facturado_bis = fields.Float(string="Neto Estimación con IVA:", store=True, digits=(12, 2))

    estimado_deducciones_bis = fields.Float(string="Menos Suma Deducciones:", store=True, digits=(12, 2))

    ret_neta_est_bis = fields.Float(string='', store=True, digits=(12, 2))
    sancion_bis = fields.Float(string="Sanción por Incump. de plazo:", digits=(12, 2))

    a_pagar_bis = fields.Float(string="Importe liquido:", store=True,
                               digits=(12, 2))

    @api.onchange('estimado_bis')
    def calculos_bis(self):
        self.estimacion_iva_bis = self.estimado_bis * self.b_iva
        self.estimacion_facturado_bis = self.estimacion_iva_bis + self.estimado_bis
        self.a_pagar_bis = self.estimacion_facturado_bis

    # montoreal_bis_bis = fields.Float(store=True, string='MONTO EJECUTADO REAL PARA ESTA ESTIMACION', digits=(12, 2))
    devolucion_est_bis = fields.Float(string='', store=True, digits=(12, 2))
    # MONTO PROGRAMADO PARA ESTA ESTIMACION
    monto_programado_est_bis = fields.Float(digits=(12, 2), store=True)
    diasdif_bis = fields.Integer(string='Dias de diferencia', store=True)
    dias_desfasamiento_bis = fields.Float(string='DIAS DE DESFASAMIENTO', store=True)
    monto_atraso_bis = fields.Float(string='MONTO DE ATRASO', digits=(12, 2), store=True)
    diasperiodo_bis = fields.Float(string='Dia total del periodo', store=True)
    diasest_bis = fields.Float(string='', store=True)
    diastransest_bis = fields.Float(string='', store=True)
    total_ret_est_bis = fields.Float(string='TOTAL DE LA RETENCION HASTA ESTA ESTIMACION', digits=(12, 2), store=True)
    porcentaje_est_bis = fields.Float(string='', store=True)
    porc_total_ret_bis = fields.Float(string='PORCENTAJE DE LA RETENCION TOTAL', store=True)
    # RETENCION NETA A APLICAR EN ESTA ESTIMACION
    montodiario_programado_bis = fields.Float(string='MONTO DIARIO PROGRAMADO', digits=(12, 2), store=True)
    diasrealesrelacion_bis = fields.Float(string='DIAS EJECUTADOS REALCES CON RELACION AL MONTO DIARIO PROGRAMADO',
                                      digits=(12, 2), store=True)
    montoreal_bis = fields.Float(store=True, string='MONTO EJECUTADO REAL PARA ESTA ESTIMACION', digits=(12, 2))

    @api.multi
    @api.onchange('estimado_bis')
    def penas_convencionales_bis(self):
        if not self.tipo_estimacion:
            pass
        else:
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
            b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])

            estimado_bis = self.estimado_bis
            
            # MONTO ACTUAL A EJECUTAR ESTIMADO
            acum_real = 0
            for i in b_est:
                if not self.idobra:
                    acum_real = acum_real + i.estimado
                    self.montoreal_bis = acum_real + self.estimado_bis
                elif int(i.idobra) <= int(self.idobra):
                    acum_real = acum_real + i.estimado
                    self.montoreal_bis = acum_real
                    print(acum_real, self.montoreal_bis, ' xdsds', self.estimado_bis)

            f_estimacion_inicio = self.fecha_inicio_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
            f_estimacion_termino = self.fecha_termino_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
            f_est_termino_dia = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")  # DIA DE TERMINO DE LA ESTIMACION
            # BUSCAR FECHAS DEL PROGRAMA
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
            # VERIFICAR SI EXISTE CONVENIO
            _search_cove = self.env['proceso.convenios_modificado'].search_count(
                [("nombre_contrato", "=", self.obra.nombre_contrato), ("tipo_convenio", "=", 'PL' or 'BOTH')])
            b_convenio = self.env['proceso.convenios_modificado'].search(
                [('nombre_contrato', '=', self.obra.nombre_contrato)])
            if _search_cove > 0:
                for i in b_convenio:
                    if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                        fecha_prog = datetime.strptime(str(i.plazo_fecha_inicio), "%Y-%m-%d").date()
                        fecha_inicio_programa = fecha_prog
                        fecha_prog2 = datetime.strptime(str(i.plazo_fecha_termino), "%Y-%m-%d").date()
                        fecha_termino_programa = fecha_prog2
            else:
                # FECHA INICIO Y TERMINO DEL PROGRAMA
                fecha_inicio_programa = b_programa.fecha_inicio_programa
                fecha_termino_programa = b_programa.fecha_termino_programa

            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL CONTRATO
            '''fe1 = fecha_inicio_programa
            fe2 = fecha_termino_programa
            if fe1 and fe2:
                f1h = datetime.strptime(str(fe1), "%Y-%m-%d")
                f2h = datetime.strptime(str(fe2), "%Y-%m-%d")
                rh = f2h - f1h
                self.dias_transcurridos = rh.days + 1'''

            monto_contrato = b_programa.total_programa
            # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
            diasest_bis = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
            acum = 0
            cont = 0
            # CICLO QUE RECORRE LA LISTA DE PROGRAMAS
            for i in sorted(b_programa.programa_contratos):
                cont = cont + 1
                fechatermino = i.fecha_termino
                fechainicio = i.fecha_inicio
                date_format = "%Y-%m-%d"
                # INDICAR SI ES UN PROGRAMA QUE ABARCA VARIOS MESES
                fuera_mes1 = datetime.strptime(str(fechainicio), date_format)
                fuera_mes2 = datetime.strptime(str(fechatermino), date_format)
                fuera_mesr = fuera_mes2 - fuera_mes1
                fuera_mes = fuera_mesr.days + 1
                num_months = (fechainicio.year - fechatermino.year) * 12 + (fechatermino.month - fechainicio.month)
                # fecha termino del programa, mes y año
                fecha_terminop_y_m = datetime(fecha_termino_programa.year, fecha_termino_programa.month, 1)
                # fecha termino de la estimacion mes y año
                fecha_terminoest_y_m = datetime(f_estimacion_termino.year, f_estimacion_termino.month, 1)
                # ciclo de fecha termino del programa mes y año
                f_termino_proglista = datetime(fechatermino.year, fechatermino.month, 1)
                f_termino_prog_todo = datetime(fechainicio.year, fechainicio.month, fechainicio.day)
                fecha_terminoest_todo = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                                 f_estimacion_termino.day)
                # fecha termino de estimacion mes y año
                print('CON LA ESTIMACION #', self.idobra, ' +++++')
                print('INICIA EL CICLO ******', cont)
                # SI LA FECHA DEL TERMINO DE LA ESTIMACION ES IGUAL A LA DEL PROGRAMA HACER CALCULO FINAL
                if fecha_terminop_y_m == fecha_terminoest_y_m:
                    print('FASE FINAL')
                    acum = acum + i.monto
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO REAL DEL PROGRAMA HASTA LA FECHA DE TERMINO DE LA ESTIMACION ACTUAL
                    dias = r.days
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days
                    # fecha estimacion inicio, fecha desde del dia 1
                    fei = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    # fecha termino programa
                    ftp = datetime.strptime(str(fecha_termino_programa), date_format)
                    r3 = ftp - fei
                    # Contar el numero dias del inicio de la estimacion hasta el dia del termino programa
                    d_est_programatermino = r3.days
                    # FECHA TERMINACION ESTIMACION
                    fet = datetime.strptime(str(f_estimacion_termino), date_format)
                    # FECHA TERMINO PROGRAMA
                    ftp = datetime.strptime(str(fecha_termino_programa), date_format)
                    r4 = ftp - fet
                    # Contar el numero de dias desde el termino de la estimacion hasta el termino del programa
                    d_esttermino_programa = r4.days
                    f_termino_actual = datetime.strptime(str(fechainicio), date_format)
                    f_esttermino = datetime.strptime(str(f_estimacion_termino), date_format)
                    res = f_esttermino - f_termino_actual
                    dias_trans_mesactual = res.days
                    dia_inicio_prog = datetime.strptime(str(fechatermino.replace(day=1)), date_format)
                    dia_inicio_prog2 = datetime.strptime(str(fechatermino), date_format)
                    dia_inicior = dia_inicio_prog2 - dia_inicio_prog
                    dia_inicio_atermino = dia_inicior.days
                    # ultimo monto programa entre dias hasta final programa por dias del final de estimacion
                    # hasta final de programa
                    ff = d_esttermino_programa
                    ff2 = d_est_programatermino + 1
                    # FORMULA: ULTIMO MONTO / DIA INICIO MES ESTIMACION HASTA DIA TERMINO PROGRAMA * DIA TERMINO ESTIMACION
                    # HASTA DIA TERMINO PORGRAMA

                    b_programa_c = self.env['proceso.programa'].search_count([('obra.id', '=', self.obra.id)])
                    if b_programa_c == 1:  # print('solo hay un monto')
                        monto_final = (i.monto / (dias + 1)) * ff
                        m_estimado = acum + monto_final
                    elif self.idobra == 1 or b_est_count == 0:
                        monto_final = 0
                        m_estimado = (acum - i.monto) + monto_final
                    else:
                        # monto_final = (i.monto / (dias + 1)) * ff
                        monto_final = (i.monto / (dia_inicio_atermino + 1)) * (dias_trans_mesactual + 1)
                        m_estimado = (acum - i.monto) + monto_final

                    self.diasest_bis = diasest_bis
                    self.diastransest_bis = ff2
                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_est_bis = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdif_bis = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodo_bis = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if self.montodiario_programado_bis == 0:
                        self.montodiario_programado_bis = 1
                    self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridos <= self.diasrealesrelacion_bis:
                        self.dias_desfasamiento_bis = 0
                    else:
                        self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                    # MONTO DE ATRASO
                    self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                    self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                    if self.retenido_anteriormente == 0:  # RETENCION
                        if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                            self.ret_neta_est_bis = 0
                            self.devolucion_est_bis = 0
                        else:
                            self.ret_neta_est_bis = self.total_ret_est_bis * -1
                            self.devolucion_est_bis = 0
                    elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                        self.ret_neta_est_bis = self.retenido_anteriormente * -1
                        self.devolucion_est_bis = self.retenido_anteriormente * -1
                    elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                        self.ret_neta_est_bis = 0
                        self.devolucion_est_bis = 0
                    elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                        self.devolucion_est_bis = 0
                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                    elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                        self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis

                # SI EL PROGRAMA ES UNICO Y DE VARIOS MESES
                elif int(num_months) > 2:
                    print(' FUERA DE MES', num_months)
                    acum = acum + i.monto
                    # dias transcurridos
                    f_termino_esti = datetime.strptime(str(f_estimacion_termino), date_format)
                    f_inicio_prog = datetime.strptime(str(fecha_inicio_programa), date_format)
                    r_diastrans = f_termino_esti - f_inicio_prog
                    dias_trans = r_diastrans.days + 1
                    m_estimado = (acum / fuera_mes) * dias_trans
                    self.diastransest_bis = dias_trans
                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_est_bis = m_estimado
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                    # TERMINO DE LA ESTIMACION
                    dias = r.days + 1
                    self.diasdif_bis = dias

                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    # DIAS DEL PERIODO
                    total_dias_periodo = r2.days
                    self.diasperiodo_bis = total_dias_periodo

                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridos <= self.diasrealesrelacion_bis:
                        self.dias_desfasamiento_bis = 0
                    else:
                        self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                    # MONTO DE ATRASO
                    self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                    self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                    if self.retenido_anteriormente == 0:  # RETENCION
                        if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                            self.ret_neta_est_bis = 0
                            self.devolucion_est_bis = 0
                        else:
                            self.ret_neta_est_bis = self.total_ret_est_bis * -1
                            self.devolucion_est_bis = 0
                    elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                        self.ret_neta_est_bis = self.retenido_anteriormente * -1
                        self.devolucion_est_bis = self.retenido_anteriormente * -1
                    elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                        self.ret_neta_est_bis = 0
                        self.devolucion_est_bis = 0
                    elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                        self.devolucion_est_bis = 0
                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                    elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                        self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis

                # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
                elif f_est_termino_dia.day == diasest_bis:
                    # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                    if fechatermino <= self.fecha_termino_estimacion:
                        acum = acum + i.monto
                        print('CUANDO LA ESTIMACION ES IGUAL AL DIA DEL ULTIMO MES')
                        f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                        f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r = f2 - f1
                        dias = r.days  # DIAS DE DIFERENCIA ENTRE EST
                        f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                        f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                        r2 = f4 - f3
                        total_dias_periodo = r2.days  # TOTAL DIAS PERIODO PROGRAMA
                        diasest_bis = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                        f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                        f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r4 = f8 - f7
                        diastransest_bis = r4.days
                        m_estimado = acum
                        self.diasest_bis = diasest_bis
                        self.diastransest_bis = diastransest_bis
                        self.monto_programado_est_bis = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                        self.diasdif_bis = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                        self.diasperiodo_bis = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                        self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis  # MONTO DIARIO PROGRAMADO
                        if self.montodiario_programado_bis == 0:  # DIAS EJECUTADOS REALES
                            self.montodiario_programado_bis = 1  # CON RELACION AL
                        self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis  # MONTO DIARIO PROGRAMADO
                        if self.dias_transcurridos <= self.diasrealesrelacion_bis:  # DIAS DE DESFASAMIENTO
                            self.dias_desfasamiento_bis = 0
                        else:
                            self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                        self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis  # MONTO DE ATRASO
                        self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                        self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis  # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                        if self.retenido_anteriormente == 0:  # RETENCION
                            if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                                self.ret_neta_est_bis = 0
                                self.devolucion_est_bis = 0
                            else:
                                self.ret_neta_est_bis = self.total_ret_est_bis * -1
                                self.devolucion_est_bis = 0
                        elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                            self.ret_neta_est_bis = self.retenido_anteriormente * -1
                            self.devolucion_est_bis = self.retenido_anteriormente * -1
                        elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                            self.ret_neta_est_bis = 0
                            self.devolucion_est_bis = 0
                        elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                            self.devolucion_est_bis = 0
                            self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                        elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                            self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                            self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                    else:
                        print('FUERA DE FECHA')
                # SI EL TERMINO DE LA ESTIMACION ES MENOR AL DIA TOTAL DEL MES ENTONCES SE MODIFICARA EL MONTO ACUMULADO
                # CON UNA FORMULA PARA CALCULAR EL MONTO ACTUAL HASTA LA FECHA DE TERMINO DE LA ESTIMACION
                elif f_est_termino_dia.day < diasest_bis:
                    if f_termino_proglista > fecha_terminoest_y_m:
                        print('se paso de fecha 2')
                    # SON MESES DIFERENTES
                    elif f_estimacion_inicio.month is not f_estimacion_termino.month:
                        print('#1 EL MES FECHA EST INICIO ES DIFERENTE AL MES EST TERMINO')
                        esti = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
                        if fecha_terminoest_y_m == fecha_terminop_y_m:
                            for x in esti:
                                if int(x.idobra) > int(self.idobra) or int(x.idobra) > (b_est_count + 1):
                                    # SI NO ES LA ULTIMA ESTIMACION ENTONCES
                                    pass
                                elif x.idobra == self.idobra or int(x.idobra) == (b_est_count + 1):
                                    print('#2 COINCIDE CON EL ULTIMO MES DEL PROGRAMA CUANDO SON MESES DIFERENTES')
                                    diasest_bisx = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                        1]
                                    fx = datetime.strptime(str(f_estimacion_inicio), date_format)
                                    fy = datetime.strptime(str(f_estimacion_termino), date_format)
                                    rx = fy - fx
                                    diastransest_bisx = rx.days  # DIAS TRANSCURRIDOS DE LA ESTIMACION
                                    ultimo_monto = i.monto  # MONTO CORRESPONDIENTE A LA FECHA DE ESTIMACION CON LA DEL PROGRAMA
                                    x1 = acum - ultimo_monto
                                    x2 = i.monto / diasest_bisx
                                    m_estimado = x1 + x2 * (diastransest_bisx + 1)
                                    self.diasest_bis = diasest_bisx
                                    self.diastransest_bis = diastransest_bisx
                                    self.monto_programado_est_bis = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                    r = f2 - f1
                                    dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE
                                    self.diasdif_bis = dias  # HASTA EL TERMINO DE LA ESTIMACION
                                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                                    r2 = f4 - f3
                                    total_dias_periodo = r2.days
                                    self.diasperiodo_bis = total_dias_periodo  # DIAS DEL PERIODO
                                    self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis  # MONTO DIARIO PROGRAMADO
                                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                    self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                                    if self.dias_transcurridos <= self.diasrealesrelacion_bis:
                                        self.dias_desfasamiento_bis = 0
                                    else:
                                        self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis  # DIAS DE DESFASAMIENTO
                                    self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis  # MONTO DE ATRASO
                                    self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                    self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                                    self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                                    if self.retenido_anteriormente == 0:  # RETENCION
                                        if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                                            self.ret_neta_est_bis = 0
                                            self.devolucion_est_bis = 0
                                        else:
                                            self.ret_neta_est_bis = self.total_ret_est_bis * -1
                                            self.devolucion_est_bis = 0
                                    elif (
                                            self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                                        self.ret_neta_est_bis = self.retenido_anteriormente * -1
                                        self.devolucion_est_bis = self.retenido_anteriormente * -1
                                    elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                                        self.ret_neta_est_bis = 0
                                        self.devolucion_est_bis = 0
                                    elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                                        self.devolucion_est_bis = 0
                                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                    elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                                        self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                        self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                            print('prosigue')
                            pass
                        else:
                            acum = acum + i.monto
                            f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                            f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                            r = f2 - f1
                            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA TERMINO EST
                            dias = r.days
                            f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                            f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                            r2 = f4 - f3
                            # DIAS DEL PERIODO
                            total_dias_periodo = r2.days

                            # ---------------------
                            # CUANTOS DIAS TIENE EL MES DE LA FECHA ESTIMADA
                            diasest_bis = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[1]
                            dia_mes_termino = \
                            calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]

                            dat = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                           f_estimacion_termino.day)
                            dat4 = datetime(f_estimacion_inicio.year, f_estimacion_inicio.month,
                                            f_estimacion_inicio.day)
                            dat2 = datetime(fechatermino.year, fechatermino.month, fechatermino.day)

                            f_sansion = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                                 fecha_termino_programa.day)
                            # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MAYOR A LA FECHA DEL TERMINO DEL PROGRAMA
                            if dat > dat2:
                                print('CUANDO LA FECHA DE TERMINO DE EST ES MAYOR A LA DEL TERMINO DEL PROGRAMA')
                                cx = 0
                                acum_ftemtp = 0
                                for c in b_programa.programa_contratos:
                                    dat3 = datetime(c.fecha_termino.year,
                                                    c.fecha_termino.month,
                                                    c.fecha_termino.day)
                                    if dat == dat3:
                                        print('fin')
                                    elif dat3 > dat:
                                        print('terminar')
                                    elif dat3 <= dat:
                                        acum_ftemtp += c.monto
                                        print('acumular')
                                        cx += 1
                                    '''elif dat4 > f_sansion:
                                        print('SANSION TERMINAR')'''

                                ultimo_monto = b_programa.programa_contratos[int(cx)].monto

                                f_pt = datetime.strptime(str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                                         date_format)
                                f_et = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = f_et - f_pt
                                d_entre_fecha = ry.days

                                ff_inicio = datetime.strptime(str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                                              date_format)
                                ff_termino = datetime.strptime(
                                    str(b_programa.programa_contratos[int(cx)].fecha_termino), date_format)
                                rf = ff_termino - ff_inicio
                                diastransest_bisx = rf.days + 1
                                formula = (ultimo_monto / diastransest_bisx) * (d_entre_fecha + 1)
                                acumulado = acum_ftemtp
                                m_estimado = acumulado + formula  # * (diastransest_bis + 1)
                                self.ultimomonto = ultimo_monto
                                self.diasest_bis = diasest_bis
                                self.diastransest_bis = diastransest_bisx
                                self.monto_programado_est_bis = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                self.diasdif_bis = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                                self.diasperiodo_bis = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                                self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis  # MONTO DIARIO PROGRAMADO
                                if self.montodiario_programado_bis == 0:
                                    self.montodiario_programado_bis = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                                # DIAS DE DESFASAMIENTO
                                if self.dias_transcurridos <= self.diasrealesrelacion_bis:
                                    self.dias_desfasamiento_bis = 0
                                else:
                                    self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                                self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis  # MONTO DE ATRASO
                                self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                                self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                                if self.retenido_anteriormente == 0:  # RETENCION
                                    if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                                        self.ret_neta_est_bis = 0
                                        self.devolucion_est_bis = 0
                                    else:
                                        self.ret_neta_est_bis = self.total_ret_est_bis * -1
                                        self.devolucion_est_bis = 0
                                elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                                    self.ret_neta_est_bis = self.retenido_anteriormente * -1
                                    self.devolucion_est_bis = self.retenido_anteriormente * -1
                                elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                                    self.ret_neta_est_bis = 0
                                    self.devolucion_est_bis = 0
                                elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                                    self.devolucion_est_bis = 0
                                    self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                                    self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                    self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                    # return acumulado
                            # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MENOR A LA FECHA DEL TERMINO DEL PROGRAMA
                            elif dat < dat2:
                                print('#5 ES NORMAL')
                                ultimo_monto = i.monto
                                ffx = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                                ffx2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = ffx2 - ffx
                                diastransest_bis = ry.days + 1
                                _programa_cx = self.env['proceso.programa'].search_count(
                                    [('obra.id', '=', self.obra.id)])
                                if _programa_cx == 1:
                                    x1 = acum
                                else:
                                    x1 = acum - ultimo_monto
                                # formula = (i.monto / dia_mes_termino) * (dia_mes_termino - diastransest_bis) # cambio el 09/04/20
                                formula = (i.monto / dia_mes_termino) * diastransest_bis  # SIDUR-ED-19-078.1698
                                if _programa_cx == 1:
                                    m_estimado = x1 - formula
                                else:
                                    m_estimado = x1 + formula
                                self.ultimomonto = ultimo_monto
                                self.diasest_bis = diasest_bis
                                self.diastransest_bis = diastransest_bis
                                self.monto_programado_est_bis = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                self.diasdif_bis = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                                self.diasperiodo_bis = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                                self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis  # MONTO DIARIO PROGRAMADO
                                if self.montodiario_programado_bis == 0:
                                    self.montodiario_programado_bis = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                                if self.dias_transcurridos <= self.diasrealesrelacion_bis:  # DIAS DE DESFASAMIENTO
                                    self.dias_desfasamiento_bis = 0
                                else:
                                    # self.dias_desfasamiento_bis = self.dias_transcurridos - self.diasrealesrelacion_bis
                                    self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                                self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis  # MONTO DE ATRASO
                                self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                                self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                                if self.retenido_anteriormente == 0:  # RETENCION
                                    if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                                        self.ret_neta_est_bis = 0
                                        self.devolucion_est_bis = 0
                                    else:
                                        self.ret_neta_est_bis = self.total_ret_est_bis * -1
                                        self.devolucion_est_bis = 0
                                elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                                    self.ret_neta_est_bis = self.retenido_anteriormente * -1
                                    self.devolucion_est_bis = self.retenido_anteriormente * -1
                                elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                                    self.ret_neta_est_bis = 0
                                    self.devolucion_est_bis = 0
                                elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                                    self.devolucion_est_bis = 0
                                    self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                                    self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                                    self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis

                                    # elif f_termino_proglista <= fecha_terminoest_y_m:
                    elif f_termino_prog_todo <= fecha_terminoest_todo:
                        acum = acum + i.monto
                        print('CUANDO LA ESTIMACION ES MENOS DE 30 DIAS EN EL MES')
                        f1 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                        f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r = f2 - f1
                        dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO
                        dia_0 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                        dia_02 = datetime.strptime(str(f_estimacion_inicio), date_format)
                        dia_r = dia_02 - dia_0
                        dia_rr = dia_r.days  # dia 0 del mes al dia de inicio de esti
                        dia_inicioprog = datetime.strptime(str(fechainicio.replace(day=1)), date_format)
                        dia_terminprog = datetime.strptime(str(fechatermino), date_format)
                        dia_progx = dia_terminprog - dia_inicioprog
                        dia_progy = dia_progx.days + 1
                        fg = datetime.strptime(str(f_estimacion_inicio), date_format)
                        fh = datetime.strptime(str(f_estimacion_termino), date_format)
                        rx = fh - fg
                        # DIAS TRANSCURRIDOS DE LA ESTIMACION
                        diasx = rx.days + 1
                        # DIAS DEL PERIODO
                        f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                        f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                        r2 = f4 - f3
                        total_dias_periodo = r2.days
                        # ---------------------
                        # DIAS DEL MES DE LA ESTIMACION
                        diasest_bis = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                        f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                        f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r4 = f8 - f7
                        # DIAS DESDE EL INICIO DEL MES DE LA ESTIMACION HASTA EL TERMINO
                        diastransest_bis = r4.days + 1
                        # -------------------------
                        # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                        if fechatermino < f_estimacion_termino:
                            formula = 1  # evitar errores
                        else:
                            if diastransest_bis == diasest_bis:
                                print(' termina en el dia ultimo del mes', diastransest_bis, diasest_bis)
                                # MONTO / DIAS DEL MES * NUMERO DE DIAS TRANSCURRIDOS DEL INICIO DEL MES DE LA EST AL TERMINO
                                formula = (i.monto / diasest_bis) * diastransest_bis
                            elif dia_progy < diasest_bis:
                                print(' TERMINO PROG ES ANTES DEL MES')
                                formula = (i.monto / dia_progy) * diasx  # SIDUR-PF-18-220.1497
                            else:
                                # normal
                                print(' termina antes', diastransest_bis, diasest_bis)
                                # formula = (i.monto / (diasest_bis - dia_rr)) * diasx
                                # formula = (i.monto / diasest_bis) * diasx
                                formula = (i.monto / diasest_bis) * dias  # SIDUR-ED-20-002.1873

                        self.ultimomonto = i.monto
                        if str(self.idobra) == '1' or int(b_est_count) == 0:
                            m_estimado = formula
                        else:
                            m_estimado = (acum - i.monto) + formula  # (i.monto - formula)
                        self.diasest_bis = diasest_bis
                        self.diastransest_bis = diastransest_bis + 1
                        fv = datetime.strptime(str(fecha_inicio_programa), date_format)
                        fvv = datetime.strptime(str(f_estimacion_termino), date_format)
                        rxx = fvv - fv
                        diasf = rxx.days
                        self.monto_programado_est_bis = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                        self.diasdif_bis = diasf + 1  # DIAS DE DIFERENCIA ENTRE EST
                        self.diasperiodo_bis = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                        self.montodiario_programado_bis = self.monto_programado_est_bis / self.diasdif_bis  # MONTO DIARIO PROGRAMADO
                        # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                        if self.montodiario_programado_bis == 0:
                            self.montodiario_programado_bis = 1
                        self.diasrealesrelacion_bis = self.montoreal_bis / self.montodiario_programado_bis
                        if self.dias_transcurridos <= self.diasrealesrelacion_bis:  # DIAS DE DESFASAMIENTO
                            self.dias_desfasamiento_bis = 0
                        else:
                            self.dias_desfasamiento_bis = self.diasdif_bis - self.diasrealesrelacion_bis
                        self.monto_atraso_bis = self.dias_desfasamiento_bis * self.montodiario_programado_bis  # MONTO DE ATRASO
                        # PORCENTAJE ESTIMADO
                        self.porcentaje_est_bis = (m_estimado / monto_contrato) * 100
                        # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        self.porc_total_ret_bis = self.retencion * self.dias_desfasamiento_bis
                        self.total_ret_est_bis = (self.monto_atraso_bis * self.porc_total_ret_bis) / 100
                        if self.retenido_anteriormente == 0:  # RETENCION
                            if self.montoreal_bis > self.monto_programado_est_bis:  # SI NO ES RET NI DEV
                                self.ret_neta_est_bis = 0
                                self.devolucion_est_bis = 0
                            else:
                                self.ret_neta_est_bis = self.total_ret_est_bis * -1
                                self.devolucion_est_bis = 0
                        elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est_bis == 0:  # DEVOLUCION
                            self.ret_neta_est_bis = self.retenido_anteriormente * -1
                            self.devolucion_est_bis = self.retenido_anteriormente * -1
                        elif self.retenido_anteriormente == 0 and self.total_ret_est_bis == 0:
                            self.ret_neta_est_bis = 0
                            self.devolucion_est_bis = 0
                        elif (self.retenido_anteriormente * -1) <= self.total_ret_est_bis:  # RETENCION
                            self.devolucion_est_bis = 0
                            self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                        elif (self.retenido_anteriormente * -1) > self.total_ret_est_bis:  # DEVOLUCION
                            self.ret_neta_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                            self.devolucion_est_bis = (self.retenido_anteriormente * -1) - self.total_ret_est_bis
                    else:
                        print('no x2')
                else:
                    print('se termino el cliclo xxxxxxxxxxxxxxxxxxx')
