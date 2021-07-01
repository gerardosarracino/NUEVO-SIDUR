# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date
from datetime import datetime
import calendar
import warnings


class EstimacionesBis(models.Model):
    _inherit = 'control.estimaciones'

    estimacion_bis = fields.Many2one('control.estimaciones', string="Selecciona estimacion Bis")

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

    estimado_bis_related = fields.Float('Estimado Bis', related="estimacion_bis.estimado")

    @api.multi
    @api.onchange('estimado_bis')
    def calculos_bis(self):
        self.estimado = self.estimado_bis
        self.estimacion_subtotal = self.estimado_bis
        self.estimacion_iva = self.estimacion_subtotal * self.b_iva
        self.estimacion_facturado = self.estimacion_iva + self.estimacion_subtotal
        # SACAR VALOR DEDUCCIONES
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })
            if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                rec.update({
                    'valor': self.sub_total_esc_h * rec.porcentaje / 100
                })
        # SUMA DE DEDUCCIONES
        sumax = 0
        for i in self.deducciones:
            resultado = i.valor
            sumax = sumax + resultado
        self.estimado_deducciones = sumax
        self.a_pagar = self.estimacion_facturado - self.estimado_deducciones

    '''@api.multi
    @api.onchange('estimado_bis')
    def calculos_bis(self):

        self.estimacion_iva_bis = self.estimado_bis * self.b_iva
        self.estimacion_facturado_bis = self.estimacion_iva_bis + self.estimado_bis
        self.a_pagar_bis = self.estimacion_facturado_bis

        self.estimado = self.estimado_bis
        self.estimacion_subtotal = self.estimado_bis
        self.estimacion_iva = self.estimacion_subtotal * self.b_iva
        self.estimacion_facturado = self.estimacion_iva + self.estimacion_subtotal
        # SACAR VALOR DEDUCCIONES
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })
            if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                rec.update({
                    'valor': self.sub_total_esc_h * rec.porcentaje / 100
                })
        # SUMA DE DEDUCCIONES
        sumax = 0
        for i in self.deducciones:
            resultado = i.valor
            sumax = sumax + resultado
        self.estimado_deducciones = sumax
        self.a_pagar = self.estimacion_facturado - self.estimado_deducciones

        for rec in self.estimacion_bis:
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', rec.obra.id)])
            b_est = self.env['control.estimaciones'].search([('obra.id', '=', rec.obra.id)])
            # ACUMULAMOS RETENIDOS ANTERIORES
            acum_Ret = 0
            for i in b_est:
                if not rec.idobra:
                    if not i.idobra:
                        break
                    else:
                        acum_Ret += i.ret_neta_est
                else:
                    if int(rec.idobra) <= int(i.idobra):
                        pass
                    else:
                        acum_Ret += i.ret_neta_est
            # SACAMOS EL TOTAL ESTIMADO DE LOS CONCEPTOS
            suma = 0
            for i in rec.conceptos_partidas:
                resultado = i.importe_ejecutado
                suma = suma + resultado
            # ESCALATORIA
            if rec.tipo_estimacion == '2' or rec.tipo_estimacion == '3':
                rec.write({
                    'estimado': rec.sub_total_esc_h,
                })
                suma = rec.sub_total_esc_h
            else:
                rec.write({
                    'estimado': suma,
                })
            # MONTO ACTUAL A EJECUTAR ESTIMADO
            if b_est_count == 0:
                if not rec.idobra:
                    rec.write({
                        'montoreal': suma,
                    })
            else:
                acum_real = 0
                for i in b_est:
                    if not rec.idobra:
                        acum_real += + i.estimado
                        rec.write({
                            'montoreal': acum_real + rec.estimado,
                        })
                    elif int(rec.idobra) == 1:
                        if b_est_count > 1:
                            acum_real += i.estimado
                            rec.write({
                                'montoreal': acum_real + rec.estimado,
                            })
                        else:
                            acum_real += i.estimado
                            rec.write({
                                'montoreal': rec.estimado,
                            })
                    elif int(i.idobra) < int(rec.idobra):
                        acum_real += i.estimado
                        rec.write({
                            'montoreal': acum_real + rec.estimado,
                        })

            # RETENIDO ANTERIORMENTE
            rec.write({
                'retenido_anteriormente': acum_Ret,
            })

            if int(b_est_count) == 0 or int(rec.idobra) == 1:
                rec.write({
                    'retenido_anteriormente': 0,
                })
            # INDICA SI ES NUEVA ESTIMACION, NO IMPORTADA DE SIDEOP PARA CONDICION DE QWEB
            rec.write({
                'nuevo_metodo': True,
            })
            f_estimacion_inicio = rec.fecha_inicio_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
            f_estimacion_termino = rec.fecha_termino_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
            f_est_termino_dia = datetime.strptime(str(f_estimacion_termino),
                                                  "%Y-%m-%d")  # DIA DE TERMINO DE LA ESTIMACION
            # BUSCAR FECHAS DEL PROGRAMA
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', rec.obra.id)])
            # VERIFICAR SI EXISTE CONVENIO
            _search_cove = self.env['proceso.convenios_modificado'].search_count(
                [("nombre_contrato", "=", rec.obra.nombre_contrato),
                 ("tipo_convenio", "=", 'PL' or 'BOTH')])
            b_convenio = self.env['proceso.convenios_modificado'].search(
                [('nombre_contrato', '=', rec.obra.nombre_contrato)])
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
            if fecha_inicio_programa and fecha_termino_programa:
                f1h = datetime.strptime(str(fecha_inicio_programa), "%Y-%m-%d")
                f2h = datetime.strptime(str(fecha_termino_programa), "%Y-%m-%d")
                rh = f2h - f1h
                rec.write({
                    'dias_transcurridos': rh.days + 1,
                })

            monto_contrato = b_programa.total_programa
            # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
            diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
            rec.write({
                'diasest': diasest,
            })
            acum = 0
            cont = 0
            date_format = "%Y-%m-%d"
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
                    monto_final = 0
                    b_programa_c = self.env['proceso.programa'].search_count([('obra.id', '=', rec.obra.id)])
                    if b_programa_c == 1:  # print('solo hay un monto')
                        # monto_final = (i.monto / (dias + 1)) * ff
                        m_estimado = m_estimado = (i.monto / (total_dias_periodo + 1)) * (dias_trans_mesactual + 1)
                    elif rec.idobra == 1 or b_est_count == 0:
                        monto_final = 0
                        m_estimado = (acum - i.monto) + monto_final
                    else:
                        # monto_final = (i.monto / (dias + 1)) * ff
                        monto_final = (i.monto / (dia_inicio_atermino + 1)) * (dias_trans_mesactual + 1)
                        m_estimado = (acum - i.monto) + monto_final

                    if fechatermino < f_estimacion_termino:
                        m_estimado = acum

                    rec.write({
                        'ultimomonto': monto_final,
                    })
                    rec.write({
                        'diasest': diasest,
                    })
                    rec.write({
                        'diastransest': ff2,
                    })
                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    rec.write({
                        'monto_programado_est': m_estimado,
                    })
                    # DIAS DE DIFERENCIA ENTRE EST
                    rec.write({
                        'diasdif': dias + 1,
                    })
                    # TOTAL DIAS PERIODO PROGRAMA
                    rec.write({
                        'diasperiodo': total_dias_periodo,
                    })
                    # MONTO DIARIO PROGRAMADO
                    rec.write({
                        'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                    })
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if rec.montodiario_programado == 0:
                        rec.write({
                            'montodiario_programado': 1,
                        })
                    rec.write({
                        'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                    })
                    if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                        rec.write({
                            'dias_desfasamiento': 0,
                        })
                    else:
                        rec.write({
                            'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                        })
                    # MONTO DE ATRASO
                    rec.write({
                        'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                    })
                    # PORCENTAJE ESTIMADO
                    rec.write({
                        'porcentaje_est': (m_estimado / monto_contrato) * 100,
                    })
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    rec.write({
                        'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                    })
                    rec.write({
                        'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                    })
                    if rec.retenido_anteriormente == 0:  # RETENCION
                        if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                            rec.write({
                                'ret_neta_est': 0,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                        else:
                            rec.write({
                                'ret_neta_est': rec.total_ret_est * -1,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                    elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                        rec.write({
                            'ret_neta_est': rec.retenido_anteriormente * -1,
                        })
                        rec.write({
                            'devolucion_est': rec.retenido_anteriormente * -1,
                        })
                    elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                        rec.write({
                            'ret_neta_est': 0,
                        })
                        rec.write({
                            'devolucion_est': 0,
                        })
                    elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                        rec.write({
                            'devolucion_est': 0,
                        })
                        rec.write({
                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })
                    elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                        rec.write({
                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })
                        rec.write({
                            'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })

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
                    rec.write({
                        'diastransest': dias_trans,
                    })
                    if fechatermino < f_estimacion_termino:
                        m_estimado = acum

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    rec.write({
                        'monto_programado_est': m_estimado,
                    })
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                    # TERMINO DE LA ESTIMACION
                    dias = r.days + 1
                    rec.write({
                        'diasdif': dias,
                    })

                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    # DIAS DEL PERIODO
                    total_dias_periodo = r2.days
                    rec.write({
                        'diasperiodo': total_dias_periodo,
                    })

                    # MONTO DIARIO PROGRAMADO
                    rec.write({
                        'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                    })
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    rec.write({
                        'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                    })
                    if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                        rec.write({
                            'dias_desfasamiento': 0,
                        })
                    else:
                        rec.write({
                            'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                        })
                    # MONTO DE ATRASO
                    rec.write({
                        'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                    })
                    # PORCENTAJE ESTIMADO
                    rec.write({
                        'porcentaje_est': (m_estimado / monto_contrato) * 100,
                    })
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    rec.write({
                        'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                    })
                    rec.write({
                        'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                    })
                    if rec.retenido_anteriormente == 0:  # RETENCION
                        if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                            rec.write({
                                'ret_neta_est': 0,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                        else:
                            rec.write({
                                'ret_neta_est': rec.total_ret_est * -1,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                    elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                        rec.write({
                            'ret_neta_est': rec.retenido_anteriormente * -1,
                        })
                        rec.write({
                            'devolucion_est': rec.retenido_anteriormente * -1,
                        })
                    elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                        rec.write({
                            'ret_neta_est': 0,
                        })
                        rec.write({
                            'devolucion_est': 0,
                        })
                    elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                        rec.write({
                            'devolucion_est': 0,
                        })
                        rec.write({
                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })
                    elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                        rec.write({
                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })
                        rec.write({
                            'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                        })

                # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
                elif f_est_termino_dia.day == diasest:
                    # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                    if fechatermino <= rec.fecha_termino_estimacion:
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
                        diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                        f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                        f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r4 = f8 - f7
                        diastransest = r4.days
                        m_estimado = acum
                        rec.write({
                            'diasest': diasest,
                        })
                        rec.write({
                            'diastransest': diastransest,
                        })
                        rec.write({
                            'monto_programado_est': m_estimado,
                        })
                        rec.write({
                            'diasdif': dias + 1,
                        })
                        rec.write({
                            'diasperiodo': total_dias_periodo,
                        })
                        rec.write({
                            'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                        })
                        if rec.montodiario_programado == 0:  # DIAS EJECUTADOS REALES
                            rec.write({
                                'montodiario_programado': 1,
                            })
                        rec.write({
                            'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                        })
                        if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                            rec.write({
                                'dias_desfasamiento': 0,
                            })
                        else:
                            rec.write({
                                'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                            })

                        rec.write({
                            'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                        })
                        rec.write({
                            'porcentaje_est': (m_estimado / monto_contrato) * 100,
                        })
                        rec.write({
                            'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                        })
                        rec.write({
                            'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                        })

                        if rec.retenido_anteriormente == 0:  # RETENCION
                            if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                                rec.write({
                                    'ret_neta_est': 0,
                                })
                                rec.write({
                                    'devolucion_est': 0,
                                })
                            else:
                                rec.write({
                                    'ret_neta_est': rec.total_ret_est * -1,
                                })
                                rec.write({
                                    'devolucion_est': 0,
                                })
                        elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                            rec.write({
                                'ret_neta_est': rec.retenido_anteriormente * -1,
                            })
                            rec.write({
                                'devolucion_est': rec.retenido_anteriormente * -1,
                            })
                        elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                            rec.write({
                                'ret_neta_est': 0,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                        elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                            rec.write({
                                'devolucion_est': 0,
                            })
                            rec.write({
                                'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                        elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                            rec.write({
                                'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                            rec.write({
                                'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                    else:
                        print('FUERA DE FECHA')
                # SI EL TERMINO DE LA ESTIMACION ES MENOR AL DIA TOTAL DEL MES ENTONCES SE MODIFICARA EL MONTO ACUMULADO
                # CON UNA FORMULA PARA CALCULAR EL MONTO ACTUAL HASTA LA FECHA DE TERMINO DE LA ESTIMACION
                elif f_est_termino_dia.day < diasest:
                    if f_termino_proglista > fecha_terminoest_y_m:
                        print('se paso de fecha 2')
                    # SON MESES DIFERENTES
                    elif f_estimacion_inicio.month is not f_estimacion_termino.month:
                        print('#1 EL MES FECHA EST INICIO ES DIFERENTE AL MES EST TERMINO')
                        esti = self.env['control.estimaciones'].search([('obra.id', '=', rec.obra.id)])
                        if fecha_terminoest_y_m == fecha_terminop_y_m:
                            for x in esti:
                                if int(x.idobra) > int(rec.idobra) or int(x.idobra) > (b_est_count + 1):
                                    # SI NO ES LA ULTIMA ESTIMACION ENTONCES
                                    pass
                                elif x.idobra == rec.idobra or int(x.idobra) == (b_est_count + 1):
                                    print('#2 COINCIDE CON EL ULTIMO MES DEL PROGRAMA CUANDO SON MESES DIFERENTES')
                                    diasestx = \
                                        calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                            1]
                                    fx = datetime.strptime(str(f_estimacion_inicio), date_format)
                                    fy = datetime.strptime(str(f_estimacion_termino), date_format)
                                    rx = fy - fx
                                    diastransestx = rx.days  # DIAS TRANSCURRIDOS DE LA ESTIMACION
                                    ultimo_monto = i.monto  # MONTO CORRESPONDIENTE A LA FECHA DE ESTIMACION CON LA DEL PROGRAMA
                                    x1 = acum - ultimo_monto
                                    x2 = i.monto / diasestx
                                    m_estimado = x1 + x2 * (diastransestx + 1)

                                    if fechatermino < f_estimacion_termino:
                                        m_estimado = acum

                                    rec.write({
                                        'diasest': diasestx,
                                    })
                                    rec.write({
                                        'diastransest': diastransestx,
                                    })
                                    rec.write({
                                        'monto_programado_est': m_estimado,
                                    })
                                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                    r = f2 - f1
                                    dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE
                                    rec.write({
                                        'diasdif': dias,
                                    })
                                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                                    r2 = f4 - f3
                                    total_dias_periodo = r2.days
                                    rec.write({
                                        'diasperiodo': total_dias_periodo,
                                    })
                                    rec.write({
                                        'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                                    })
                                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                    rec.write({
                                        'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                                    })
                                    if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                        rec.write({
                                            'dias_desfasamiento': 0,
                                        })
                                    else:
                                        rec.write({
                                            'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                                        })
                                    rec.write({
                                        'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                                    })
                                    rec.write({
                                        'porcentaje_est': (m_estimado / monto_contrato) * 100,
                                    })
                                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                    rec.write({
                                        'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                                    })
                                    rec.write({
                                        'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                                    })

                                    if rec.retenido_anteriormente == 0:  # RETENCION
                                        if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                                            rec.write({
                                                'ret_neta_est': 0,
                                            })
                                            rec.write({
                                                'devolucion_est': 0,
                                            })
                                        else:
                                            rec.write({
                                                'ret_neta_est': rec.total_ret_est * -1,
                                            })
                                            rec.write({
                                                'devolucion_est': 0,
                                            })
                                    elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                                        rec.write({
                                            'ret_neta_est': rec.retenido_anteriormente * -1,
                                        })
                                        rec.write({
                                            'devolucion_est': rec.retenido_anteriormente * -1,
                                        })
                                    elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                                        rec.write({
                                            'ret_neta_est': 0,
                                        })
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                    elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                        rec.write({
                                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                        })
                                    elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                                        rec.write({
                                            'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                        })
                                        rec.write({
                                            'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                        })
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
                            diasest = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[1]
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
                                u_m = 0
                                fecha_inicio_aux = ''
                                fecha_termino_aux = ''
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
                                        u_m = c.monto
                                        fecha_inicio_aux = c.fecha_inicio
                                        fecha_termino_aux = c.fecha_termino

                                ultimo_monto = u_m  # b_programa.programa_contratos[int(cx)].monto

                                f_pt = datetime.strptime(str(fecha_inicio_aux), date_format)
                                f_et = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = f_et - f_pt
                                d_entre_fecha = ry.days

                                ff_inicio = datetime.strptime(str(fecha_inicio_aux),
                                                              date_format)
                                ff_termino = datetime.strptime(str(fecha_termino_aux), date_format)
                                rf = ff_termino - ff_inicio
                                diastransestx = rf.days + 1
                                formula = (ultimo_monto / diastransestx) * (d_entre_fecha + 1)
                                acumulado = acum_ftemtp
                                if fechatermino < f_estimacion_termino:
                                    m_estimado = acumulado
                                else:
                                    m_estimado = acumulado + formula

                                rec.write({
                                    'ultimomonto': ultimo_monto,
                                })
                                rec.write({
                                    'diasest': diasest,
                                })
                                rec.write({
                                    'diastransest': diastransestx,
                                })
                                rec.write({
                                    'monto_programado_est': m_estimado,
                                })
                                rec.write({
                                    'diasdif': dias + 1,
                                })
                                rec.write({
                                    'diasperiodo': total_dias_periodo,
                                })
                                rec.write({
                                    'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                                })
                                if rec.montodiario_programado == 0:
                                    rec.write({
                                        'montodiario_programado': 1,
                                    })
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                diasrealesrelacion = rec.montoreal / rec.montodiario_programado
                                rec.write({
                                    'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                                })
                                if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                    rec.write({
                                        'dias_desfasamiento': 0,
                                    })
                                else:
                                    rec.write({
                                        'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                                    })
                                rec.write({
                                    'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                                })
                                rec.write({
                                    'porcentaje_est': (m_estimado / monto_contrato) * 100,
                                })
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                rec.write({
                                    'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                                })
                                rec.write({
                                    'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                                })
                                if rec.retenido_anteriormente == 0:  # RETENCION
                                    if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                                        rec.write({
                                            'ret_neta_est': 0,
                                        })
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                    else:
                                        rec.write({
                                            'ret_neta_est': rec.total_ret_est * -1,
                                        })
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                                    rec.write({
                                        'ret_neta_est': rec.retenido_anteriormente * -1,
                                    })
                                    rec.write({
                                        'devolucion_est': rec.retenido_anteriormente * -1,
                                    })
                                elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                                    rec.write({
                                        'ret_neta_est': 0,
                                    })
                                    rec.write({
                                        'devolucion_est': 0,
                                    })
                                elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                                    rec.write({
                                        'devolucion_est': 0,
                                    })
                                    rec.write({
                                        'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })
                                elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                                    rec.write({
                                        'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })
                                    rec.write({
                                        'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })
                                    # return acumulado
                            # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MENOR A LA FECHA DEL TERMINO DEL PROGRAMA
                            elif dat < dat2:
                                print('#5 ES NORMAL')
                                ultimo_monto = i.monto
                                ffx = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                                ffx2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = ffx2 - ffx
                                diastransest = ry.days + 1
                                _programa_cx = self.env['proceso.programa'].search_count(
                                    [('obra.id', '=', rec.obra.id)])
                                if _programa_cx == 1:
                                    x1 = acum
                                else:
                                    x1 = acum - ultimo_monto
                                # formula = (i.monto / dia_mes_termino) * (dia_mes_termino - diastransest) # cambio el 09/04/20
                                formula = (i.monto / dia_mes_termino) * diastransest  # SIDUR-ED-19-078.1698
                                if _programa_cx == 1:
                                    m_estimado = x1 - formula
                                else:
                                    m_estimado = x1 + formula

                                if fechatermino < f_estimacion_termino:
                                    m_estimado = acum

                                rec.write({
                                    'ultimomonto': ultimo_monto,
                                })
                                rec.write({
                                    'diasest': diasest,
                                })
                                rec.write({
                                    'diastransest': diastransest,
                                })
                                rec.write({
                                    'monto_programado_est': m_estimado,
                                })
                                rec.write({
                                    'diasdif': dias + 1,
                                })
                                rec.write({
                                    'diasperiodo': total_dias_periodo,
                                })
                                rec.write({
                                    'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                                })
                                if rec.montodiario_programado == 0:
                                    rec.write({
                                        'montodiario_programado': 1,
                                    })
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                rec.write({
                                    'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                                })

                                if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                    rec.write({
                                        'dias_desfasamiento': 0,
                                    })
                                else:
                                    rec.write({
                                        'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                                    })
                                rec.write({
                                    'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                                })
                                rec.write({
                                    'porcentaje_est': (m_estimado / monto_contrato) * 100,
                                })
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                rec.write({
                                    'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                                })
                                rec.write({
                                    'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                                })
                                if rec.retenido_anteriormente == 0:  # RETENCION
                                    if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                                        rec.write({
                                            'ret_neta_est': 0,
                                        })
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                    else:
                                        rec.write({
                                            'ret_neta_est': rec.total_ret_est * -1,
                                        })
                                        rec.write({
                                            'devolucion_est': 0,
                                        })
                                elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                                    rec.write({
                                        'ret_neta_est': rec.retenido_anteriormente * -1,
                                    })
                                    rec.write({
                                        'devolucion_est': rec.retenido_anteriormente * -1,
                                    })
                                elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                                    rec.write({
                                        'ret_neta_est': 0,
                                    })
                                    rec.write({
                                        'devolucion_est': 0,
                                    })
                                elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                                    rec.write({
                                        'devolucion_est': 0,
                                    })
                                    rec.write({
                                        'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })
                                elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                                    rec.write({
                                        'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })
                                    rec.write({
                                        'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                                    })

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
                        diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                        f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                        f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r4 = f8 - f7
                        # DIAS DESDE EL INICIO DEL MES DE LA ESTIMACION HASTA EL TERMINO
                        diastransest = r4.days + 1
                        # -------------------------
                        # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                        if fechatermino < f_estimacion_termino:
                            formula = 1  # evitar errores
                        else:
                            if diastransest == diasest:
                                print(' termina en el dia ultimo del mes', diastransest, diasest)
                                # MONTO / DIAS DEL MES * NUMERO DE DIAS TRANSCURRIDOS DEL INICIO DEL MES DE LA EST AL TERMINO
                                formula = (i.monto / diasest) * diastransest
                            elif dia_progy < diasest:
                                print(' TERMINO PROG ES ANTES DEL MES')
                                formula = (i.monto / dia_progy) * diasx  # SIDUR-PF-18-220.1497
                            else:
                                # normal
                                print(' termina antes', diastransest, diasest)
                                # formula = (i.monto / (diasest - dia_rr)) * diasx
                                # formula = (i.monto / diasest) * diasx
                                formula = (i.monto / diasest) * dias  # SIDUR-ED-20-002.1873

                        rec.write({
                            'ultimomonto': i.monto,
                        })
                        if str(rec.idobra) == '1' or int(b_est_count) == 0:
                            m_estimado = formula
                        else:
                            m_estimado = (acum - i.monto) + formula  # (i.monto - formula)

                        if fechatermino < f_estimacion_termino:
                            m_estimado = acum

                        rec.write({
                            'diasest': diasest,
                        })
                        rec.write({
                            'diastransest': diastransest + 1,
                        })
                        fv = datetime.strptime(str(fecha_inicio_programa), date_format)
                        fvv = datetime.strptime(str(f_estimacion_termino), date_format)
                        rxx = fvv - fv
                        diasf = rxx.days
                        rec.write({
                            'monto_programado_est': m_estimado,
                        })
                        rec.write({
                            'diasdif': diasf + 1,
                        })
                        rec.write({
                            'diasperiodo': total_dias_periodo,
                        })
                        rec.write({
                            'montodiario_programado': rec.monto_programado_est / rec.diasdif,
                        })
                        # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                        if rec.montodiario_programado == 0:
                            rec.write({
                                'montodiario_programado': 1,
                            })
                        rec.write({
                            'diasrealesrelacion': rec.montoreal / rec.montodiario_programado,
                        })
                        if rec.diasdif <= rec.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                            rec.write({
                                'dias_desfasamiento': 0,
                            })
                        else:
                            rec.write({
                                'dias_desfasamiento': rec.diasdif - rec.diasrealesrelacion,
                            })

                        rec.write({
                            'monto_atraso': rec.dias_desfasamiento * rec.montodiario_programado,
                        })
                        # PORCENTAJE ESTIMADO
                        rec.write({
                            'porcentaje_est': (m_estimado / monto_contrato) * 100,
                        })
                        # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        rec.write({
                            'porc_total_ret': rec.retencion * rec.dias_desfasamiento,
                        })
                        rec.write({
                            'total_ret_est': (rec.monto_atraso * rec.porc_total_ret) / 100,
                        })
                        if rec.retenido_anteriormente == 0:  # RETENCION
                            if rec.montoreal > rec.monto_programado_est:  # SI NO ES RET NI DEV
                                rec.write({
                                    'ret_neta_est': 0,
                                })
                                rec.write({
                                    'devolucion_est': 0,
                                })
                            else:
                                rec.write({
                                    'ret_neta_est': rec.total_ret_est * -1,
                                })
                                rec.write({
                                    'devolucion_est': 0,
                                })
                        elif (rec.retenido_anteriormente * -1) > 0 and rec.total_ret_est == 0:  # DEVOLUCION
                            rec.write({
                                'ret_neta_est': rec.retenido_anteriormente * -1,
                            })
                            rec.write({
                                'devolucion_est': rec.retenido_anteriormente * -1,
                            })
                        elif rec.retenido_anteriormente == 0 and rec.total_ret_est == 0:
                            rec.write({
                                'ret_neta_est': 0,
                            })
                            rec.write({
                                'devolucion_est': 0,
                            })
                        elif (rec.retenido_anteriormente * -1) <= rec.total_ret_est:  # RETENCION
                            rec.write({
                                'devolucion_est': 0,
                            })
                            rec.write({
                                'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                        elif (rec.retenido_anteriormente * -1) > rec.total_ret_est:  # DEVOLUCION
                            rec.write({
                                'ret_neta_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                            rec.write({
                                'devolucion_est': (rec.retenido_anteriormente * -1) - rec.total_ret_est,
                            })
                    else:
                        print('no x2')
                else:
                    print('se termino el cliclo xxxxxxxxxxxxxxxxxxx')
            print('---------------------------------xcxxxxxxxxxxxxxxxxxx-------------------------------')
            # --------... DATOS PARA SANCION ...-----------
            # BUSCAR FECHAS DEL PROGRAMA
            # b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
            # VERIFICAR SI EXISTE CONVENIO

            fechaterminosancion = ""
            for i in b_programa.programa_contratos:
                fechaterminosancion = i.fecha_termino
                fecha_termino_programa = i.fecha_termino

            estimacion_search = self.env['control.estimaciones'].search([('obra', '=', rec.obra.id)])
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', rec.obra.id)])
            f_estimacion_termino = rec.fecha_termino_estimacion
            # X-X-X-X-X-X-X-X-X--X  SANCION ------------------------------------------------------
            if f_estimacion_termino > fechaterminosancion:  # SANCION ///////////////////////////////////////////
                print(' APLICAR SANCION JUNTO ESTIMACION FINIQUITO')
                acum_ret = 0
                termino_periodo_s = datetime.strptime(str(fecha_termino_programa), "%Y-%m-%d")
                termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
                for u in estimacion_search:
                    if int(u.idobra) <= int(rec.idobra) or int(u.idobra) <= int(b_est_count + 1):
                        if u.ret_neta_est < 0:
                            acum_ret += u.ret_neta_est
                        else:
                            pass
                        if u.sancion > 0:
                            acum_ret = 0
                    else:
                        pass
                resta = termino_estimacion_s - termino_periodo_s
                dias_sancion = resta.days
                if dias_sancion == 0:
                    dias_sancion = 1
                sancion = rec.estimado * dias_sancion * 0.001
                rec.write({
                    'sancion': sancion,
                })
                rec.write({
                    'dias_atraso_sancion': dias_sancion,
                })
                acum_ret_est = 0
                ret_anteriores = rec.ret_neta_est
            else:
                rec.write({
                    'sancion': 0,
                })
                rec.write({
                    'dias_atraso_sancion': 0,
                })

            # --------... TERMINA DATOS PARA SANCION ...-----------

            if rec.si_aplica_estimacion:
                acum_ret_est = 0
                for i in estimacion_search:
                    if int(i.idobra) >= int(rec.idobra):
                        pass
                    else:
                        acum_ret_est += i.ret_neta_est

                rec.write({
                    'ret_neta_est': (acum_ret_est * -1),
                })
                rec.write({
                    'devolucion_est': (acum_ret_est * -1),
                })
            # SACAR VALOR DEDUCCIONES
            for dec in rec.deducciones:
                print(rec.estimado, dec.porcentaje, ' xxxxxxxxxxxxxxxxxx')
                dec.write({
                    'valor': rec.estimado * dec.porcentaje / 100
                })
                if rec.tipo_estimacion == '3' or rec.tipo_estimacion == '2':
                    dec.write({
                        'valor': rec.sub_total_esc_h * dec.porcentaje / 100
                    })
            # SUMA DE DEDUCCIONES
            sumax = 0
            for i in rec.deducciones:
                resultado = i.valor
                sumax = sumax + resultado
                rec.estimado_deducciones = sumax

            if rec.si_aplica_amortizar == True:  # VERIFICAR SI APLICA AMORTIZACION
                # CALCULAR ESTIMACION NETA SIN IVA
                if rec.sub_total_esc > 0:
                    rec.write({
                        'estimacion_subtotal': rec.sub_total_esc_h,
                    })
                else:
                    rec.write({
                        'estimacion_subtotal': rec.estimado - rec.amort_anticipo,
                    })

                # METODO PARA CALCULAR ESTIMACION IVA.
                rec.write({
                    'estimacion_iva': (rec.estimado - rec.amort_anticipo) * rec.b_iva,
                })

                # METODO PARA CALCULAR ESTIMACION + IVA
                rec.write({
                    'estimacion_facturado': rec.estimacion_subtotal + rec.estimacion_iva,
                })
                # IMPORTE LIQUIDO
                if rec.tipo_estimacion == '3' or rec.tipo_estimacion == '2':
                    rec.write({
                        'sancion': 0,
                    })
                    rec.write({
                        'devolucion_est': 0,
                    })
                    rec.write({
                        'ret_neta_est': 0,
                    })
                if rec.sancion > 0:
                    rec.write({
                        # SE SANCION
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) - (
                            rec.sancion) + rec.devolucion_est - (rec.ret_neta_est * -1)
                    })
                elif rec.retenido_anteriormente <= rec.total_ret_est:
                    rec.write({
                        # SE RETIENE
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) - (
                                rec.ret_neta_est * -1)
                    })

                elif rec.retenido_anteriormente > rec.total_ret_est:
                    # SE DEVUELVE
                    rec.write({
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) + rec.devolucion_est
                    })

                # AMORTIZACION ANTICIPO
                acum_amort = 0
                print(' AMORTIZIPO AQui')
                for x in estimacion_search:
                    if not rec.idobra:
                        acum_amort += x.amort_anticipo
                    elif int(rec.idobra) > int(x.idobra):
                        acum_amort += x.amort_anticipo
                    elif int(rec.idobra) < int(x.idobra):
                        pass
                if rec.idobra == '':
                    rec.write({
                        'amort_anticipo': rec.obra.anticipo_a - acum_amort,
                    })
                else:
                    rec.write({
                        'amort_anticipo': rec.obra.anticipo_a - acum_amort,
                    })
            else:
                print(' AMORT NORMAL')
                # self.amort_anticipo = self.amort_anticipo_partida * self.estimado
                acum_amort = 0
                for x in estimacion_search:
                    if not rec.idobra:
                        acum_amort += x.amort_anticipo
                    elif int(rec.idobra) < int(x.idobra):
                        pass
                    elif int(rec.idobra) > int(x.idobra):
                        acum_amort += x.amort_anticipo
                if not rec.idobra:

                    amort_actual = (rec.amort_anticipo_partida * rec.estimado)
                    acum_amortizado = acum_amort + amort_actual
                    if acum_amortizado >= float(rec.obra.anticipo_a):
                        rec.write({
                            'amort_anticipo': rec.obra.anticipo_a - acum_amort,
                        })
                    elif float(rec.obra.anticipo_a) == float(acum_amort):
                        rec.write({
                            'amort_anticipo': 0,
                        })
                    else:
                        rec.write({
                            'amort_anticipo': (rec.amort_anticipo_partida * rec.estimado),
                        })
                else:

                    if acum_amort >= float(rec.obra.anticipo_a):
                        rec.write({
                            'amort_anticipo': 0,
                        })
                    elif float(rec.obra.anticipo_a) == float(acum_amort):
                        rec.write({
                            'amort_anticipo': 0,
                        })
                    else:
                        if float(rec.amort_anticipo + acum_amort) > float(rec.obra.anticipo_a):
                            # acum_total_anti = acum_amort
                            rec.write({
                                'amort_anticipo': rec.obra.anticipo_a - acum_amort,
                            })
                        else:
                            rec.write({
                                'amort_anticipo': (rec.amort_anticipo_partida * rec.estimado),
                            })

                # CALCULAR ESTIMACION NETA SIN IVA
                if rec.sub_total_esc > 0:
                    rec.write({
                        'estimacion_subtotal': rec.sub_total_esc_h,
                    })
                else:
                    rec.write({
                        'estimacion_subtotal': rec.estimado - rec.amort_anticipo,
                    })
                rec.write({
                    'estimacion_iva': (rec.estimado - rec.amort_anticipo) * rec.b_iva,
                })
                rec.write({
                    'estimacion_facturado': rec.estimacion_subtotal + rec.estimacion_iva,
                })
                # IMPORTE LIQUIDO
                if rec.sancion > 0:
                    print('IMPORTE LIQUIDO CON SANSION')
                    rec.write({
                        # SE RETIENE
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) + rec.devolucion_est - rec.sancion
                    })
                elif rec.retenido_anteriormente <= rec.total_ret_est:
                    rec.write({
                        # SE RETIENE
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) - (rec.ret_neta_est * -1)
                    })

                elif rec.retenido_anteriormente > rec.total_ret_est:
                    # SE DEVUELVE
                    rec.write({
                        'a_pagar': (rec.estimacion_facturado - rec.estimado_deducciones) + rec.devolucion_est
                    })

        if self.estimado_bis > 0:
            self.estimacion_iva_bis = self.estimado_bis * self.b_iva
            self.estimacion_facturado_bis = self.estimacion_iva_bis + self.estimado_bis
            self.a_pagar_bis = self.estimacion_facturado_bis

            self.estimado = self.estimado_bis
            self.estimacion_subtotal = self.estimado_bis
            self.estimacion_iva = self.estimacion_subtotal * self.b_iva
            self.estimacion_facturado = self.estimacion_iva + self.estimacion_subtotal
            # SACAR VALOR DEDUCCIONES
            for rec in self.deducciones:
                rec.update({
                    'valor': self.estimado * rec.porcentaje / 100
                })
                if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                    rec.update({
                        'valor': self.sub_total_esc_h * rec.porcentaje / 100
                    })
            # SUMA DE DEDUCCIONES
            sumax = 0
            for i in self.deducciones:
                resultado = i.valor
                sumax = sumax + resultado
            self.estimado_deducciones = sumax
            self.a_pagar = self.estimacion_facturado - self.estimado_deducciones

            for rec in self.estimacion_bis:
                for dec in rec.deducciones:
                    dec.write({
                        'valor': (rec.estimado - self.estimado) * dec.porcentaje / 100
                    })

                suma2 = 0
                for i in rec.deducciones:
                    resultado = i.valor
                    suma2 = suma2 + resultado

                estimado = rec.estimado - self.estimado
                estimacion_subtotal = (rec.estimado - self.estimado) - rec.amort_anticipo
                estimacion_iva = ((rec.estimado - self.estimado) - rec.amort_anticipo) * self.b_iva
                estimacion_facturado = estimacion_subtotal + estimacion_iva# (((rec.estimado - self.estimado) - rec.amort_anticipo) * self.b_iva) + (rec.estimado - self.estimado)
                print(rec.estimacion_subtotal, rec.estimacion_iva)
                rec.write({
                    'estimado': estimado,
                    'estimacion_subtotal': estimacion_subtotal,
                    'estimacion_iva': estimacion_iva,
                    'estimacion_facturado': estimacion_facturado,
                    'estimado_deducciones': suma2,
                })

                if rec.sancion > 0:
                    rec.write({
                        # SE SANCION
                        'a_pagar': (estimacion_facturado - suma2) - rec.sancion + rec.devolucion_est - (rec.ret_neta_est * -1)
                    })
                elif rec.retenido_anteriormente <= rec.total_ret_est:
                    rec.write({
                        # SE RETIENE
                        'a_pagar': (estimacion_facturado - suma2) - (rec.ret_neta_est * -1)
                    })

                elif rec.retenido_anteriormente > rec.total_ret_est:
                    # SE DEVUELVE
                    rec.write({
                        'a_pagar': (estimacion_facturado - suma2) + rec.devolucion_est
                    })'''

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


