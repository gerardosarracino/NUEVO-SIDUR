from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class Frente(models.Model):
    _name = 'proceso.frente'
    _rec_name = 'nombre'

    nombre = fields.Char(string='FRENTE')
    id_sideop = fields.Integer()
    id_partida = fields.Many2one('partidas.partidas')
    # one_m2 = fields.One2many(comodel_name="proceso.rc", inverse_name="frente")


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

    auxiliar_actividad = fields.Boolean('auxiliar que indica si fue agregada una actividad', store=True)
    numeracion = fields.Integer("Numeracion para acomodo de frentes y actividades", store=True)

    @api.model
    def create(self, values):
        # res = super(ruta_critica, self).create(values)
        b_partida = self.env['partidas.partidas'].browse(values['id_partida'])
        b_ruta = self.env['proceso.rc'].search([('id_partida.id', '=', b_partida.id)], order='numeracion asc')
        if values['auxiliar_actividad'] is False: # es frente
            auxiliar = False
            for value in b_ruta:
                b_rt = self.env['proceso.rc'].browse(value['id'])
                print(value['frente'], ' -----', values['frente'], b_rt.frente.id)
                if values['frente'] == b_rt.frente.id:
                    print('YA ESTA EL FRENTE EN LA TABLA NO SE PUEDE AGREGAR')
                    auxiliar = True
                    raise Warning(_("No se puede volver a agregar un frente que ya existe en la tabla"))

            if auxiliar is False:
                res = super(ruta_critica, self).create(values)
                b_rc = self.env['proceso.rc'].browse(res.id)
                count_ruta = self.env['proceso.rc'].search_count([('id_partida.id', '=', res.id_partida.id)])
                print('no tenia el frente agregar')
                datosn = {
                    'numeracion': count_ruta
                }
                r = b_rc.write(datosn)
                datos = {
                    'ruta_critica': [[4, res.id, {}]]
                }
                tabla = b_partida.update(datos)
        else:
            res = super(ruta_critica, self).create(values)
            b_ruta = self.env['proceso.rc'].search([('id_partida.id', '=', res.id_partida.id)],
                                                   order='numeracion asc')
            b_ruta_count = self.env['proceso.rc'].search_count(
                [('id_partida.id', '=', res.id_partida.id), ('frente.id', '=', res.frente.id)])
            b_rc = self.env['proceso.rc'].browse(res.id)
            # print('es actividad agregar debajo de su categoria en orden descendente')
            porcentaje = 0
            for value in b_ruta:
                porcentaje += value['porcentaje_est']
            if values['name']:
                count_acum = 0
                count = 0
                count_despues = 0
                count_confirmar = 0
                for value in b_ruta:# b_partida.ruta_critica:
                    count_acum += 1
                    print('entra', value['name'], count_acum)
                    if count_confirmar == 1:
                        if value['id'] == res.id:
                            print(value['name'], value['numeracion'], 'dxxxx')
                            pass
                        else:
                            count_despues += 1
                            print('entra aqui despues de agregar', count_despues)
                            datos = {
                                'numeracion': count_acum + 1
                            }
                            r = value.write(datos)

                    if value['frente'] == res.frente and value['id'] != res.id:  # es misma categoria agregar actividad aqui
                        count += 1
                        print('mismo frente', count)
                        if count == (b_ruta_count-1):
                            count_confirmar += 1
                            print('se agrega frente', count)
                            datos = {
                                'numeracion': count_acum + 1
                            }
                            r = b_rc.write(datos)

                            datos = {
                                'ruta_critica': [[4, res.id, {}]]
                            }
                            tabla = b_partida.update(datos)
            datos = {
                'total_': porcentaje
            }
            r = b_partida.write(datos)
        return res

    @api.multi
    def borrar(self):
        print(self.frente, '---', self.name)
        id_frente = self.frente.id
        id_partida = self.id_partida.id
        porcentaje_est = self.porcentaje_est
        if not self.auxiliar_actividad: # es frente, al borrar frente que borre todas sus actividades!
            print('frente quitar')
            b_rutas_frentes = self.env['proceso.rc'].search([('frente.id', '=', id_frente)])
            for i in b_rutas_frentes:
                i.unlink()
            '''b_frente = self.env['proceso.frente'].search([('id', '=', id_frente)])
            for i in b_frente:
                i.unlink()'''
        else: # es actividad
            print('actividad quitar')
            self.env['proceso.rc'].search([('id', '=', self.id)]).unlink()
        print('llego')
        b_ruta = self.env['proceso.rc'].search([('id_partida.id', '=', id_partida)])
        porcentaje = 0
        acum = 0
        for v in b_ruta:
            acum += 1
            datos_numeracion = {
                'numeracion': acum
            }
            r = v.write(datos_numeracion)
            porcentaje += v.porcentaje_est
            print('llego', v.porcentaje_est)


        b_partida = self.env['partidas.partidas'].browse(id_partida)
        if porcentaje < 0:
            porcentaje = 0
        else:
            porcentaje = porcentaje
        datos = {
            'total_': porcentaje
        }
        r = b_partida.write(datos)

        '''if self.frente is not False and self.name is False:  # ES FRENTE
            s = self.env['proceso.rc'].search(
                [('frente', '=', self.frente.id), ('id_partida', '=', self.id_partida.id)])
            print(s, 'es frente')
            for i in s:
                i.unlink()
                print(i)
        else:  # ES ACTIVIDAD
            self.env['proceso.rc'].search([('id', '=', self.id)]).unlink()
            print('es act')'''

    @api.multi
    def agregar_frentes_actividades(self):
        print('hola')
        # search = self.env['project.project'].search([('id', '=', self.project_id.id)])
        form = self.env.ref('supervision_obra.concepto_ruta_critica_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ruta critica',
            'res_model': 'proceso.rc',
            'view_mode': 'form',
            'target': 'new',
            # 'domain': [('proyecto_id', '=', self.project_id.id)],
            # 'view_id': view.id,
            'context': {'default_frente': self.frente.id, 'default_id_partida': self.id_partida.id,
                        'default_auxiliar_actividad': True},
            'views': [
                (form.id, 'form'),
            ],
            # 'res_id': search.id,  # (view.id, 'form')
        }

    @api.multi
    def unlink(self):
        return super(ruta_critica, self).unlink()


class ruta_critica_avance(models.Model):
    _name = 'proceso.rc_a'
    _rec_name = 'frente'

    auxiliar_actividad = fields.Boolean('auxiliar que indica si fue agregada una actividad', store=True)
    numeracion = fields.Integer("Numeracion para acomodo de frentes y actividades", store=True)

    id_sideop = fields.Integer()
    numero_contrato = fields.Many2one('partidas.partidas')
    numero_informe = fields.Integer(string="Numero Informe Origen")
    frente = fields.Many2one('proceso.frente', string='FRENTE', )

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
    descripcion = fields.Char(string='Descripción', required=True)
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
    # _inherit = 'mail.thread'
    _rec_name = 'numero_contrato'

    aux_imagenes = fields.Boolean(string="")  # BORRAR

    # dato import
    num_avance = fields.Integer(compute="numero_avance", store=True)

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
    residente_obra = fields.Many2many('res.users', 'name', string='Residente obra:',
                                      related="numero_contrato.residente_obra")
    ruta_critica = fields.Many2many('proceso.rc_a')

    total_ = fields.Float()
    avance_financiero = fields.Float(string="% Financiero", compute="avance_fin", store=True, digits=(12, 2))

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
    porcentaje_estimado = fields.Float(store=True, digits=(12, 2))
    fecha_actual = fields.Date(string='Fecha', required=True)
    comentarios_generales = fields.Text(string='Comentarios generales')
    situacion_contrato = fields.Selection([
        ('bien', "1- Bien"),
        ('satisfactorio', "2- Satisfactorio"),
        ('regular', "3- Regular"),
        ('deficiente', "4- Deficiente"),
        ('mal', "5- Mal")], default='bien', string="Situación del contrato")

    com_avance_obra = fields.Text()

    porcentajeProgramado = fields.Float(store=True, digits=(12, 2))

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

    @api.model
    def create(self, values):
        res = super(informe_avance, self).create(values)
        b_partida = self.env['partidas.partidas'].browse(res.numero_contrato.id)
        if not values['fecha_actual'] or res.numero_contrato.nombre_partida == 'SIDUR-PF-17-227.987':
            pass
        else:
            r_porcentaje_est = 0
            r_avance_fisico = 0
            resultado = 0
            for vals in res.ruta_critica:
                r_porcentaje_est += float(vals['porcentaje_est'])
                r_avance_fisico += float(vals['avance_fisico_ponderado'])
                resultado = (r_porcentaje_est * r_avance_fisico) / 100

            programa = self.env['programa.programa_obra']
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', b_partida.id)])
            b_prog = programa.browse(b_programa.id)

            if str(b_programa) == '[]':
                color = 'Verde'
                b_partida.write({'porcentajeProgramado': 0,
                                 'atraso': resultado, 'color_semaforo': color, 'a_fis': resultado
                                 })
            else:
                if str(b_prog.programa_contratos) == "Recordset('proceso.programa', [])":
                    color = 'Verde'
                    b_partida.write({'porcentajeProgramado': 0,
                                     'atraso': resultado, 'color_semaforo': color, 'a_fis': resultado
                                     })
                else:
                    porcentajeProgramado = b_partida.porcentajeProgramado
                    atraso = round(porcentajeProgramado, 2) - resultado
                    if porcentajeProgramado > 100:
                        porcentajeProgramado = 100
                        atraso = round(porcentajeProgramado, 2) - resultado
                    color = ''
                    if atraso <= 5:
                        color = 'Verde'
                    elif atraso > 5 and atraso <= 25:
                        color = 'Amarillo'
                    elif atraso > 25:
                        color = 'Rojo'
                    b_partida.write({'atraso': round(atraso, 2), 'color_semaforo': color, 'a_fis': resultado})
        return res

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
                                             'porcentaje_est': conceptos.porcentaje_est, 'numero_informe': num,
                                             'numero_contrato': self.numero_contrato.id,
                                             'auxiliar_actividad': conceptos.auxiliar_actividad,
                                             'numeracion': conceptos.numeracion,
                                             }]]
                })

        elif informe_c >= 1:
            # YA EXISTE EL PRIMERO, TRAER RUTA CRITICA CON %FISICO
            for conceptos in adirecta_id.ruta_critica:
                b_actividades_informe = self.env['proceso.rc_a'].search([('numero_contrato.id', '=', self.numero_contrato.id),
                                                                         ('frente.id', '=', conceptos.frente.id),
                                                                         ('name', '=', conceptos.name),
                                                                         ('numero_informe', '=', num-1)])
                print(b_actividades_informe, 'xxxxx')
                self.update({
                    'ruta_critica': [[0, 0, {'frente': conceptos.frente.id, 'name': conceptos.name,
                                             'porcentaje_est': conceptos.porcentaje_est, 'numero_informe': num,
                                             'avance_fisico': b_actividades_informe.avance_fisico,
                                             'avance_fisico_ponderado': (b_actividades_informe.porcentaje_est
                                                                         * b_actividades_informe.avance_fisico) / 100,
                                             'numero_contrato': self.numero_contrato.id,
                                             'auxiliar_actividad': conceptos.auxiliar_actividad,
                                             'numeracion': conceptos.numeracion,
                }]]
                })

            '''for conceptos in informe_b[int(informe_c) - 1].ruta_critica:
                self.update({
                    'ruta_critica': [[0, 0, {'frente': conceptos.frente.id, 'name': conceptos.name,
                                             'porcentaje_est': conceptos.porcentaje_est,
                                             'avance_fisico': conceptos.avance_fisico, 'numero_informe': num,
                                             'avance_fisico_ponderado': (conceptos.porcentaje_est * conceptos.avance_fisico) / 100}]]
                })'''

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

    @api.multi
    def unlink(self):
        self.ruta_critica.unlink()
        return super(informe_avance, self).unlink()


class ComentarioSupervision(models.Model):
    _name = 'comentario.supervision'
    _rec_name = 'partida'

    partida = fields.Many2one('partidas.partidas', store=True)
    fecha_registro = fields.Date('Fecha', required=True)
    comentario = fields.Text('Comentarios de Supervision', required=True)
