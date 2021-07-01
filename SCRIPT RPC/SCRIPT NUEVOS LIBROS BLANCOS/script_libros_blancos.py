import odoorpc, csv
import datetime
import calendar
from datetime import date, datetime

usuario = 'admin'
password = 'Sp1d3rb0r4s2020'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

numero_contrato_id = odoo.env['proceso.elaboracion_contrato'].search([]) # ("nombre_partida", "=", 'SIDUR-ED-15-039.8')

# obra = odoo.env['registro.programarobra'].search([])

for x in numero_contrato_id:

    '''print(' START', x.nombre_partida)
    revisado = x.reviso_expediente
    fecha_revisado = str(x.fecha_revisado_exp)
    verificado = x.verificado_expediente
    fecha_verificado = str(x.fecha_verificado_exp)
    responsable = x.responsable_revision_exp.id
    comentario = str(x.comentarios_expediente)
    existencia = float(x.porcentaje_existencia)

    datos_expediente = {
        'contrato': x.numero_contrato.id,
        'reviso_expediente': revisado,
        'fecha_revisado_exp': fecha_revisado,
        'verificado_expediente': verificado,
        'fecha_verificado_exp': fecha_verificado,
        'responsable_revision_exp': responsable,
        'comentarios_expediente': comentario,
        'porcentaje_existencia': existencia,
    }
    partida_nueva2 = nuevo_libro_blanco.create(datos_expediente)
    b_libros = odoo.env['libros.blancos'].browse(partida_nueva2)'''

    b_partida = odoo.env['proceso.elaboracion_contrato'].browse(x)
    for x in b_partida:
        print(x.contrato, ' ---------------------- ')
        b_count = odoo.env['libros.blancos'].search_count([('contrato', '=', x.id)])
        libro = odoo.env['libros.blancos']
        if b_count == 0:
            # libros_blancos = odoo.env['libros.blancos'].search([('contrato', '=', x.nombre_contrato)])
            print('NO EXISTE CREAR')

            datos_lb = {
                'contrato': x.id,
            }
            llb = libro.create(datos_lb)
            print(datos_lb)
            b_libros = odoo.env['libros.blancos'].browse(llb)

            docs = odoo.env['expediente.documentos_revision'].search([])
            for j in docs:
                b_docs = odoo.env['expediente.documentos_revision'].browse(j)
                for e in b_docs:
                    datos_tabla = {
                        'tabla_libros_blancos': [[0, 0, {
                            'numero_documento': e.numero_documento,
                            'nombre_documento': e.nombre_documento,
                            'nombre_documento_m2o': e.id,
                            'etapa': e.etapa,
                            'contrato_id': x.numero_contrato.id,
                            'libros_blancos_id': b_libros.id,
                        }]]
                    }

                    xd = b_libros.write(datos_tabla)
                    print('--xxxx--')
        else:
            print('YA EXISTE')



        '''for e in x.tabla_libros_blancos:
            print(e.numero_documento)
            docs = odoo.env['expediente.documentos_revision'].search([("numero_documento", "=", e.numero_documento)])
            for p in docs:
                datos_tabla = {
    
                    'tabla_libros_blancos': [[0, 0, {
                    'numero_documento': e.numero_documento,
                    'nombre_documento': e.nombre_documento,
                    'nombre_documento_m2o': p,
                    'etapa': e.etapa,
                    'aplica': e.aplica,
                    'existe': e.existe,
                    'Observaciones': e.Observaciones,
                    'contrato_id': x.numero_contrato.id,
                    'libros_blancos_id': partida_nueva2,
                    }]]
                }
    
                xd = b_libros.write(datos_tabla)'''

        print('exito ------------------', x.nombre_partida)

        '''for i in x.tabla_libros_blancos:
            if i.existe == 'Si':
                count_existencia += 1
            if i.aplica == 'Si':
                count_aplica += 1
            porcentaje_existencia = (count_existencia / count_aplica) * 100

            exis = {
                'porcentaje_existencia': porcentaje_existencia,
            }

            partida_nueva2 = b_partida.write(exis)
            print('exito', x.nombre_partida)'''


        '''for i in x.tabla_libros_blancos:
            if int(i.numero_documento) <= 40:
                i.update({'etapa': '1'})
            elif int(i.numero_documento) > 40 and int(i.numero_documento) <= 64:
                i.update({'etapa': '2'})
            elif int(i.numero_documento) > 64:
                i.update({'etapa': '3'})
            print(' exito', x.nombre_partida)'''

'''buscar_partida = odoo.env['partidas.partidas'].search_count(
    [("id_contrato_sideop", "=", row['num_contrato'])])'''

# Buscamos en informe de avance
# buscar_informe_avance = odoo.env['proceso.iavance'].search_count([("num_contrato", "=", row['num_contrato']), ("num_avance", "=", row['NumeroAvance'])])
    

# buscar_informe_update = odoo.env['proceso.iavance'].search_count([("id_sideop", "=", row['Id'])])

# if buscar_informe_update == 0:
# print(numero_contrato_id)


""" for x in numero_contrato_id:
    partida_obj_update = odoo.env['partidas.partidas'].browse(x)
    print(partida_obj_update.nombre_partida, ' ------------')
    
    programa = odoo.env['programa.programa_obra']
    b_programa = odoo.env['programa.programa_obra'].search([('obra.id', '=', partida_obj_update.id)])
    b_prog = programa.browse(b_programa)

    if str(b_programa) == '[]':
        pass
    else:
        if str(b_prog.programa_contratos) == "Recordset('proceso.programa', [])":
            pass
        else:
            estimacion = odoo.env['control.estimaciones'].search([("obra.id", "=", partida_obj_update.id)])
            acum = 0
            for u in estimacion:
                xd = odoo.env['control.estimaciones'].browse(u)
                
                for i in xd:
                    print('xd')
                    acum += i.a_pagar
                    total_estimado = acum

            partida_obj_update.write({'total_estimado': total_estimado
                                        })
            print('EXITO', total_estimado ) """

'''programa = odoo.env['programa.programa_obra']
    b_programa = odoo.env['programa.programa_obra'].search([('obra.id', '=', partida_obj_update.id)])
    b_prog = programa.browse(b_programa)

    if str(b_programa) == '[]':
        print(' NO TIENE PROGRAMA X')
        color = 'Rojo'
        partida_obj_update.write({'porcentajeProgramado': 0,
                                                'atraso': partida_obj_update.a_fis, 'color_semaforo': color 
                    })
    else:
        if str(b_prog.programa_contratos) == "Recordset('proceso.programa', [])":
            print(' NO TIENE PROGRAMA X')
            color = 'Rojo'
            partida_obj_update.write({'porcentajeProgramado': 0,
                                                    'atraso': partida_obj_update.a_fis, 'color_semaforo': color 
                        })
        else:

            date_format = "%Y/%m/%d"
            date_format2 = "%Y-%m-%d"
            today = date.today()
            hoy = str(today.strftime(date_format))
            
            # d1 = '2020-04-28'
            fecha_hoy = datetime.strptime(str(hoy), date_format)

            if len(hoy) == '':
                print('1')
                Prog_Del = None
            else:
                Prog_Del_ = str(hoy)
                Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

            # fecha_hoy = datetime.strptime(str(fecha_act), date_format2)

            for u in b_prog.programa_contratos:
                fecha_termino_pp = u.fecha_termino
            
                if str(fecha_termino_pp) == 'False':
                    print('NO HAY FECHA DE TERMINO')
                else:
                    fecha_termino_contrato = datetime.strptime(str(fecha_termino_pp), date_format2)

                    acumulado = 0
                    cont = 0
                    porcentajeProgramado = 0
                    # porcentajefinanciero = 0

                    for i in b_prog.programa_contratos:
                        
                        cont += 1
                        print('CICLO DEL PROGRAMA # ', cont)
                        # fecha_termino_p = datetime(i.fecha_termino.year, i.fecha_termino.month, i.fecha_termino.day)
                        fecha_termino_p = datetime.strptime(str(i.fecha_termino), date_format2)
                        # fechahoy = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)

                        if fecha_hoy > fecha_termino_contrato:
                            print(' LA FECHA DE HOY ES MAYOR A LA DE TERMINO')
                            porcentajeProgramado = 100.00
                            atraso = porcentajeProgramado - partida_obj_update.a_fis
                                
                            if atraso <= 5:
                                color = 'Verde'
                            elif atraso > 5 and atraso <= 25:
                                color = 'Amarillo'
                            elif atraso > 25:
                                color = 'Rojo'

                            partida_obj_update.write({'porcentajeProgramado': porcentajeProgramado,
                                                        'atraso': atraso, 'color_semaforo': color,
                            })
                            print('exito', porcentajeProgramado, partida_obj_update.nombre_partida)
                        # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                        if fecha_hoy <= fecha_termino_contrato:
                            print('aqui')
                            
                            # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                            fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                            print(fechainicioprog, '=====', fecha_hoy)
                            if str(fechainicioprog) <= str(fecha_hoy):
                                # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                                fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                                _fecha_actual = datetime.strptime(str(hoy), date_format)
                                r = _fecha_actual - fechainicioprog
                                dias_trans = r.days + 1
                                # print(dias_trans)
                                # DIAS DEL MES DEL PROGRAMA ACTUAL
                                # dia_mes_inicio = datetime.strptime(str(i.fecha_inicio), date_format2)
                                # print(dia_mes_inicio)
                                # dia_mes_termino = datetime.strptime(str(i.fecha_termino), date_format2)
                                # print(dia_mes_termino)
                                # r2 = dia_mes_termino - dia_mes_inicio
                                diasest = calendar.monthrange(i.fecha_inicio.year, i.fecha_inicio.month)[1]
                                dias_del_mes = diasest # r2.days + 1

                                if dias_del_mes == 0:
                                    dias_del_mes = 1
                                # print(dias_del_mes)
                                # MONTO ACUMULADO DE PROGRAMAS
                                acumulado += i.monto

                                #if str(cont) == '1':
                                #    ultimo_monto = 0
                                #else:
                                ultimo_monto = i.monto

                                # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                                # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                                # EL TOTAL DEL PROGRAMA * 100
                                print(dias_del_mes)
                                importe_diario = ((((i.monto / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto)) /
                                                    b_prog.total_programa) * 100
                                # importe_diario = ((acumulado + i.monto) / b_prog.total_programa) * 100

                                
                                if importe_diario > 100:
                                    rr = 100
                                elif importe_diario <= 100:
                                    rr = importe_diario

                                porcentajeProgramado = rr


                                atraso = porcentajeProgramado - partida_obj_update.a_fis
                                
                                if atraso <= 5:
                                    color = 'Verde'
                                elif atraso > 5 and atraso <= 25:
                                    color = 'Amarillo'
                                elif atraso > 25:
                                    color = 'Rojo'

                                partida_obj_update.write({'porcentajeProgramado': porcentajeProgramado,
                                                            'atraso': atraso, 'color_semaforo': color 
                                })
                                print('EXITO x', porcentajeProgramado, partida_obj_update.nombre_partida)
                            else:
                                pass'''

'''programa = odoo.env['programa.programa_obra'].search([])
avance_ = odoo.env['proceso.iavance'].search([])
pos_obj = odoo.env['partidas.partidas'].search([])

for x in pos_obj:
    partida_obj_update = odoo.env['partidas.partidas'].browse(x.id)

    for y in avance_:
        avance_search = odoo.env['proceso.iavance'].search([('numero_contrato.id', '=', partida_obj_update.id)])
        # b_avance = env['proceso.iavance'].browse(y.id)
        for u in avance_search:
            fecha_act = str(u.fecha_actual)

            b_programa = odoo.env['programa.programa_obra'].search([('obra.id', '=', x.id)])

            for b_prog in b_programa:

                date_format = "%Y/%m/%d"
                date_format2 = "%Y-%m-%d"
                hoy = str(fecha_act)

                if len(hoy) == '':
                    Prog_Del = None
                else:
                    Prog_Del_ = str(hoy)
                    Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + \
                               Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

                fecha_hoy = datetime.strptime(str(Prog_Del), date_format)
                # datetime(str(Prog_Del), date_format)
                if b_prog.fecha_termino_convenida is not False:
                    fecha_termino_pp = b_prog.fecha_termino_convenida
                else:
                    fecha_termino_pp = b_prog.fecha_termino_programa

                # fecha_termino_contrato = str(fecha_termino_pp)
                fecha_termino_contrato = datetime.strptime(str(fecha_termino_pp), date_format2)

                acumulado = 0
                cont = 0
                acumulado2 = 0
                porcentajeProgramado = 0
                porcentajefinanciero = 0

                for i in b_prog.programa_contratos:
                    cont += 1

                    fechahoy = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)

                    fecha_termino_p = datetime(i.fecha_termino.year, i.fecha_termino.month, i.fecha_termino.day)

                    if fecha_hoy > str(fecha_termino_pp):
                        porcentajeProgramado = 100.00
                    # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                    if fecha_hoy <= str(fecha_termino_pp):
                        # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                        if str(fecha_termino_p) <= str(fechahoy):
                            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                            fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                            fecha_actual = datetime.strptime(str(Prog_Del), date_format)
                            r = fecha_actual - fechainicioprog
                            dias_trans = r.days + 1
                            # print(dias_trans)
                            # DIAS DEL MES DEL PROGRAMA ACTUAL
                            dia_mes_inicio = datetime.strptime(str(i.fecha_inicio), date_format2)
                            # print(dia_mes_inicio)
                            dia_mes_termino = datetime.strptime(str(i.fecha_termino), date_format2)
                            # print(dia_mes_termino)
                            r2 = dia_mes_termino - dia_mes_inicio
                            dias_del_mes = r2.days + 1

                            if dias_del_mes == 0:
                                dias_del_mes = 1
                            # print(dias_del_mes)
                            # MONTO ACUMULADO DE PROGRAMAS
                            acumulado += i.monto

                            if str(cont) == '1':
                                ultimo_monto = 0
                            else:
                                ultimo_monto = i.monto

                            # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                            # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                            # EL TOTAL DEL PROGRAMA * 100
                            importe_diario = ((((i.monto / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto)) /
                                              b_prog.total_programa) * 100

                            porcentajeProgramado = importe_diario
                            partida_obj_update.write({'porcentajeProgramado': porcentajeProgramado})
                        else:
                            partida_obj_update.write({'porcentajeProgramado': porcentajeProgramado})'''

        # partida_obj_update.write({'porcentajeProgramado': x.id})