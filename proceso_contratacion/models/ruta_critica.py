from odoo import models, fields, api, exceptions
from datetime import date, datetime
import calendar
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Frente(models.Model):
    _name = 'proceso.frente'
    _rec_name = 'nombre'

    nombre = fields.Char(string='FRENTE')
    id_sideop = fields.Integer()
    id_partida = fields.Many2one('partidas.partidas')
    #one_m2 = fields.One2many(comodel_name="proceso.rc", inverse_name="frente")


class ruta_critica(models.Model):
    _name = 'proceso.rc'
    _rec_name = 'frente'
    id_partida = fields.Many2one('partidas.partidas')
    frente = fields.Many2one('proceso.frente', string='FRENTE')
    obra = fields.Many2one('registro.programarobra')
    name = fields.Char(string="ACTIVIDADES PRINCIPALES")
    porcentaje_est = fields.Float(string="P.R.C", )
    sequence = fields.Integer()
    avance_fisico = fields.Float(string="% Avance")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
 

class ruta_critica_avance(models.Model):
    _name = 'proceso.rc_a'
    _rec_name = 'frente'
    
    id_sideop = fields.Integer()
    numero_contrato = fields.Many2one('partidas.partidas')
    numero_informe = fields.Integer(string="Numero Informe Origen")
    frente = fields.Many2one('proceso.frente',string='FRENTE', )
    
    porcentaje_est = fields.Float(string="P.R.C")
    name = fields.Char(string="ACTIVIDADES PRINCIPALES", )
    sequence = fields.Integer()
    avance_fisico = fields.Float(string="% AVANCE")

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="numero_contrato.ejercicio")

    obra = fields.Many2one('registro.programarobra')
    r = fields.Many2one('proceso.iavance')
    avance_fisico_ponderado = fields.Float(string="% FISICO PONDERADO", store=True)

    @api.multi
    @api.onchange('avance_fisico')
    def avance_fisico_pon(self):
        self.avance_fisico_ponderado = (self.porcentaje_est * self.avance_fisico) / 100
            

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)


class Galeriam2m(models.Model):
    _name = 'proceso.subirgaleria'
    _rec_name = 'descripcion'

    frente = fields.Many2one('proceso.frente', string='FRENTE')
    descripcion = fields.Char(string='Descripción',required=True)
    informe_avance = fields.Many2one('proceso.iavance')
    img = fields.Binary(string='Imagen')


class GaleriaImagenes(models.Model):
    _name = 'proceso.galeria'
    _rec_name = 'informe_avance'

    id_partida = fields.Many2one('partidas.partidas', related="informe_avance.numero_contrato")
    informe_avance = fields.Many2one('proceso.iavance')
    image = fields.Many2many('proceso.subirgaleria', string="Imagen")


class informe_avance(models.Model):
    _name = 'proceso.iavance'
    name = fields.Char()
    #_inherit = 'mail.thread'
    _rec_name = 'numero_contrato'

    aux_imagenes = fields.Boolean(string="", compute="imagen_aux")

    @api.one
    def imagen_aux(self):
        contadorx = self.env['proceso.galeria'].search_count([("id_partida.id", "=", self.numero_contrato.id)])
        if contadorx > 0:
            self.aux_imagenes = True

    # dato import
    num_avance = fields.Integer(compute="numero_avance",store=True)

    # AGREGA EL NUMERO DE AVANCE
    @api.multi
    @api.depends('fecha_actual')
    def numero_avance(self):
        if self.num_avance > 0:
            pass
        else:
            count = self.env['proceso.iavance'].search_count([('numero_contrato.id', '=', self.numero_contrato.id)])
            self.num_avance = count
        
    id_sideop = fields.Integer()
    residente_obra = fields.Many2many('res.users', 'name', string='Residente obra:', related="numero_contrato.residente_obra")
    ruta_critica = fields.Many2many('proceso.rc_a')

    total_ = fields.Float()
    avance_financiero = fields.Float(string="% Financiero", compute="avance_fin", store=True, digits=(12,2))

    # CALCULA EL AVANCE FINANCIERO A LA FECHA
    @api.multi
    @api.depends('fecha_actual')
    def avance_fin(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.numero_contrato.id)])
        acum = 0
        if str(b_programa.programa_contratos) == "proceso.programa()":
            self.avance_financiero = 0
        else:
            b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.numero_contrato.id)])
            for x in b_est:
                acum += x.estimado
            self.avance_financiero = (acum / b_programa.total_programa) * 100

    fisico_ponderado = fields.Float(string="FISICO PONDERADO")
    obra = fields.Many2one('registro.programarobra', related="numero_contrato.obra")
    numero_contrato = fields.Many2one('partidas.partidas')

    num_contrato = fields.Char(string='ID contrato sideop')

    porcentaje_e = fields.Float()
    porcentaje_estimado = fields.Float(store=True, digits=(12,2))
    fecha_actual = fields.Date(string='Fecha', required=True)
    comentarios_generales = fields.Text(string='Comentarios generales')
    situacion_contrato = fields.Selection([
        ('bien', "1- Bien"),
        ('satisfactorio', "2- Satisfactorio"),
        ('regular', "3- Regular"),
        ('deficiente', "4- Deficiente"),
        ('mal', "5- Mal")], default='bien', string="Situación del contrato")

    com_avance_obra = fields.Text()

    porcentajeProgramado = fields.Float(store=True, digits=(12,2))

    @api.multi
    @api.onchange('ruta_critica', 'fecha_actual')
    def porcest(self):
        if not self.fecha_actual:
            pass
        else:
            r_porcentaje_est = 0
            r_avance_fisico = 0
            resultado = 0
            for i in self.ruta_critica:
                r_porcentaje_est += i.porcentaje_est
                r_avance_fisico += i.avance_fisico_ponderado
                resultado = (r_porcentaje_est * r_avance_fisico) / 100
            self.porcentaje_estimado = float(resultado)

    @api.multi
    @api.onchange('ruta_critica', 'fecha_actual')
    def porProgramado(self):
        if not self.fecha_actual or self.numero_contrato.nombre_partida == 'SIDUR-PF-17-227.987':
            pass
        else:
            r_porcentaje_est = 0
            r_avance_fisico = 0
            resultado = 0
            for i in self.ruta_critica:
                r_porcentaje_est += i.porcentaje_est
                r_avance_fisico += i.avance_fisico_ponderado
                resultado = (r_porcentaje_est * r_avance_fisico) / 100

            b_partida = self.env['partidas.partidas'].browse(self.numero_contrato.id)
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.numero_contrato.id)])

            date_format = "%Y/%m/%d"
            date_format2 = "%Y-%m-%d"
            today = date.today()
            hoy = str(today.strftime(date_format))

            # d1 = '2020-04-28'
            fecha_hoy = datetime.strptime(str(hoy), date_format)

            if len(hoy) == '':
                Prog_Del = None
            else:
                Prog_Del_ = str(hoy)
                Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + \
                           Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

            # fecha_hoy = datetime.strptime(str(fecha_act), date_format2)

            for u in b_programa.programa_contratos:
                fecha_termino_pp = u.fecha_termino

                if str(fecha_termino_pp) == 'False':
                    print('NO HAY FECHA DE TERMINO')
                else:
                    fecha_termino_contrato = datetime.strptime(str(fecha_termino_pp), date_format2)

                    acumulado = 0
                    cont = 0
                    porcentajeProgramado = 0
                    for i in b_programa.programa_contratos:
                        cont += 1
                        print('CICLO DEL PROGRAMA # ', cont)
                        # fecha_termino_p = datetime(i.fecha_termino.year, i.fecha_termino.month, i.fecha_termino.day)
                        fecha_termino_p = datetime.strptime(str(i.fecha_termino), date_format2)
                        # fechahoy = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)
                        if fecha_hoy > fecha_termino_contrato:
                            print(' LA FECHA DE HOY ES MAYOR A LA DE TERMINO')
                            porcentajeProgramado = 100.00
                            atraso = porcentajeProgramado - resultado
                            if atraso <= 5:
                                color = 'Verde'
                                b_partida.write({'color_semaforo': color})
                            elif atraso > 5 and atraso <= 25:
                                color = 'Amarillo'
                                b_partida.write({'color_semaforo': color})
                            elif atraso > 25:
                                color = 'Rojo'
                                b_partida.write({'color_semaforo': color})
                            self.porcentajeProgramado = porcentajeProgramado

                        # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                        if fecha_hoy <= fecha_termino_contrato:
                            # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                            fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                            if str(fechainicioprog) <= str(fecha_hoy):
                                # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                                fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                                _fecha_actual = datetime.strptime(str(hoy), date_format)
                                r = _fecha_actual - fechainicioprog
                                dias_trans = r.days + 1
                                diasest = calendar.monthrange(i.fecha_inicio.year, i.fecha_inicio.month)[1]
                                dias_del_mes = diasest  # r2.days + 1
                                if dias_del_mes == 0:
                                    dias_del_mes = 1
                                # MONTO ACUMULADO DE PROGRAMAS
                                acumulado += i.monto
                                ultimo_monto = i.monto

                                # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                                # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                                # EL TOTAL DEL PROGRAMA * 100
                                importe_diario = ((((i.monto / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto))
                                                  / b_programa.total_programa) * 100
                                if importe_diario > 100:
                                    rr = 100
                                elif importe_diario <= 100:
                                    rr = importe_diario
                                porcentajeProgramado = rr
                                self.porcentajeProgramado = rr
                                atraso = porcentajeProgramado - resultado
                                if atraso <= 5:
                                    color = 'Verde'
                                    b_partida.write({'color_semaforo': color})
                                elif atraso > 5 and atraso <= 25:
                                    color = 'Amarillo'
                                    b_partida.write({'color_semaforo': color})
                                elif atraso > 25:
                                    color = 'Rojo'
                                    b_partida.write({'color_semaforo': color})
                                estimacion = self.env['control.estimaciones'].search(
                                    [("obra.id", "=", self.numero_contrato.id)])
                                acum = 0
                                print('normal')
                                for i in estimacion:
                                    acum += i.a_pagar
                                    total_estimado = acum
                                    b_partida.write({'total_estimado': total_estimado})
                            else:
                                pass

            r_porcentaje_est = 0
            r_avance_fisico = 0
            resultado = 0
            avance_financiero = 0

            for i in self.ruta_critica:
                r_porcentaje_est += i.porcentaje_est
                r_avance_fisico += i.avance_fisico_ponderado
                resultado = (r_porcentaje_est * r_avance_fisico) / 100

            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.numero_contrato.id)])

            if not b_programa.total_programa:
                pass
            else:
                acum = 0
                if str(b_programa.programa_contratos) == "proceso.programa()":
                    avance_financiero = 0
                else:
                    b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.numero_contrato.id)])
                    for x in b_est:
                        acum += x.estimado
                    avance_financiero = (acum / b_programa.total_programa) * 100
            
            datos = {'a_fis': resultado, 'a_fin': avance_financiero, 'porcentajeProgramado': self.porcentajeProgramado,
                     'atraso': self.porcentajeProgramado - self.porcentaje_estimado}  # 'porcentajeProgramado': self.porcentajeProgramado,
            b_partida.write(datos)

    '''@api.multi
    @api.onchange('ruta_critica', 'fecha_actual')
    def _mandar_avances(self):
        if not self.fecha_actual:
            pass
        else:
            b_partida = self.env['partidas.partidas'].browse(self.numero_contrato.id)
            r_porcentaje_est = 0
            r_avance_fisico = 0
            resultado = 0

            for i in self.ruta_critica:
                r_porcentaje_est += i.porcentaje_est
                r_avance_fisico += i.avance_fisico_ponderado
                resultado = (r_porcentaje_est * r_avance_fisico) / 100

            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.numero_contrato.id)])
            acum = 0
            if str(b_programa.programa_contratos) == "proceso.programa()":
                avance_financiero = 0
            else:
                b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.numero_contrato.id)])
                for x in b_est:
                    acum += x.estimado
                avance_financiero = (acum / b_programa.total_programa) * 100

            datos = {'a_fis': resultado, 'a_fin': avance_financiero,
                     'atraso': self.porcentajeProgramado - self.porcentaje_estimado,
                     'actualizar_onchange': True} #  'porcentajeProgramado': self.porcentajeProgramado,
            x = b_partida.write(datos)'''



    # SACAR EL PORCENTAJE TOTAL FISICO DE LA TABLA RUTA CRITICA
    @api.multi
    @api.onchange('ruta_critica', 'fecha_actual')
    def suma_importe(self):
        suma = 0
        for i in self.ruta_critica:
            resultado = i.porcentaje_est
            suma += resultado
            self.total_ = suma

    # AGREGA AUTOMATICAMENTE LOS CONCEPTOS DE INFORME
    @api.multi
    @api.onchange('obra')  # if these fields are changed, call method
    def conceptosEjecutados(self):
        count = self.env['proceso.iavance'].search_count([('numero_contrato.id', '=', self.numero_contrato.id)])
        if count == 0:
            num = 1
        else:
            num = count + 1
        adirecta_id = self.env['partidas.partidas'].search([('id', '=', self.numero_contrato.id)])

        informe_c = self.env['proceso.iavance'].search_count([('numero_contrato.id', '=', self.numero_contrato.id)])
        informe_b = self.env['proceso.iavance'].search([('numero_contrato.id', '=', self.numero_contrato.id)])

        if informe_c == 0:
            # NO EXISTE, CREAR DESDE 0
            for conceptos in adirecta_id.ruta_critica:
                
                self.update({
                    'ruta_critica': [[0, 0, {'frente': conceptos.frente.id, 'name': conceptos.name,
                                             'porcentaje_est': conceptos.porcentaje_est, 'numero_informe': num}]]
                })

        elif informe_c >= 1:
            # YA EXISTE EL PRIMERO, TRAER RUTA CRITICA CON %FISICO
            for conceptos in informe_b[int(informe_c)-1].ruta_critica:
                self.update({
                    'ruta_critica': [[0, 0, {'frente': conceptos.frente.id, 'name': conceptos.name,
                                             'porcentaje_est': conceptos.porcentaje_est,
                                             'avance_fisico': conceptos.avance_fisico, 'numero_informe': num,
                                             'avance_fisico_ponderado': (conceptos.porcentaje_est * conceptos.avance_fisico) / 100}]]
                })


    @api.multi
    def galeria_imagenes(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.galeria_fotos')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.galeria'].search_count([('informe_avance.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.galeria'].search([('informe_avance.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Galeria Fotos',
                'res_model': 'proceso.galeria',
                'view_mode': 'form',
                'context': {'default_informe_avance': self.id},
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Galeria Fotos',
                'res_model': 'proceso.galeria',
                'view_mode': 'form',
                'context': {'default_informe_avance': self.id},
                'target': 'new',
                'view_id': view.id,
            }

    @api.multi
    def galeria(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.galeria_view_kanban')
        # search = self.env['proceso.subirgaleria'].search([('informe_avance.id', '=', self.id)])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Galeria',
            'res_model': 'proceso.subirgaleria',
            'view_mode': 'kanban',
            'context': {'search_default_informe_avance': self.id},
            'view_id': view.id,
        }

    @api.multi
    def galeria_imagenes(self):
        original_url = "http://sidur.galartec.com:4000/upload/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }


class ComentarioSupervision(models.Model):
    _name = 'comentario.supervision'
    _rec_name = 'partida'

    partida = fields.Many2one('partidas.partidas', store=True)
    fecha_registro = fields.Date('Fecha', required=True)
    comentario = fields.Text('Comentarios de Supervision', required=True)
