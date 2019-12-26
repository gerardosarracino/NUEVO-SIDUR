from odoo import models, fields, api, exceptions


class ProgramaObra(models.Model):
    _name = 'programa.programa_obra'
    _rec_name = 'obra'

    # IMPORTACION
    id_prog = fields.Integer(string="ID PROGRAMA", required=False, )
    # TERMINA IMPORTACION
    obra = fields.Many2one('partidas.partidas', string='Obra:', readonly=True)

    obraid = fields.Many2one('partidas.partidas', string='Obra:', readonly=True)
    obra_id = fields.Char(compute="partidaEnlace", store=True)
    obra_id2 = fields.Char(compute="partidaEnlaceId", store=True)

    fecha_inicio_programa = fields.Date('Fecha Inicio:', related="programa_contratos.fecha_inicio", store=True)
    fecha_termino_programa = fields.Date('Fecha Término:', compute="fechaTermino", store=True)
    monto_programa_aux = fields.Float(compute='SumaProgramas')
    restante_programa = fields.Float(string="Restante:", compute='DiferenciaPrograma')

    programa_contratos = fields.Many2many('proceso.programa', string="Agregar Periodo:")

    razon = fields.Text(string="Versión:", required=False, default="")
    # MONTO DE LA PARTIDA
    monto_sinconvenio = fields.Float(string="Total Contrato sin Convenio", compute="BmontoContrato")
    # TOTAL DEL PROGRAMA CON O SIN CONVENIO
    total_partida = fields.Float(string="Total", compute="TotalPrograma") # related="obra.total_catalogo"

    select_tipo = [('Monto', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:", store=True)
    # VERIFICAR SI EXISTE CONVENIO MODIFICATORIO
    count_convenio = fields.Integer(compute="TotalPrograma")

    total_programa = fields.Float(compute="totalPrograma", store=True)

    estatus_programa = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    @api.one
    @api.depends('programa_contratos')
    def totalPrograma(self):
        acum = 0
        for i in self.programa_contratos:
            acum = acum + i.monto
            self.total_programa = acum
            print(self.total_programa)

    '''@api.multi
    def write(self, values):
        print('--')
        if self.total_programa == self.total_partida:
            print('si pasa')
        else:
            print('3')
            raise exceptions.Warning('El monto del programa no es igual al del contrato!!!,')
        # values['idobra'] = str(num)
        print('-----')
        return super(ProgramaObra, self).write(values)'''

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_programa': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_programa': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_programa': 'validado'})

    '''@api.multi
    def write(self, values):
        if not self.tipo:
            raise exceptions.Warning('Haz realizado una modificación al programa!!!,')
        elif not self.razon:
            raise exceptions.Warning('Haz realizado una modificación al programa!!!,'
                                     ' Porfavor escriba la razon del cambio.')
                 if self.restante_programa == 0:
            print('si')
        else:
            raise exceptions.Warning('el monto!!!,')
        version = self.env['programa.programa_version']
        id_programa = self.id
        datos = {'comentario': values['razon'], 'programa': id_programa, 'tipo': values['tipo']}
        nueva_version = version.create(datos)
        values['razon'] = ""
        values['tipo'] = ""
        return super(ProgramaObra, self).write(values)'''

    @api.one
    def partidaEnlace(self):
        self.obra_id = self.obra

    @api.one
    def partidaEnlaceId(self):
        self.obra_id2 = self.obraid

    @api.multi
    @api.onchange('total_partida')
    def BmontoContrato(self):
        b_partida = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])
        self.monto_sinconvenio = b_partida.monto_sin_iva

    @api.one
    @api.depends('total_partida', 'programa_contratos')
    def TotalPrograma(self):
        count_convenio = self.env['proceso.convenios_modificado'].search_count([('contrato.id', '=', self.obra.id)])
        self.count_convenio = count_convenio
        importe_convenio = self.env['proceso.convenios_modificado'].search([('contrato.id', '=', self.obra.id)])
        b_partida = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])
        if count_convenio >= 1:
            for i in importe_convenio:
                self.total_partida = i.monto_importe
        else:
            self.total_partida = self.monto_sinconvenio

    @api.multi
    @api.onchange('programa_contratos')
    def SumaProgramas(self):
        suma = 0
        for i in self.programa_contratos:
            resultado = i.monto
            suma = suma + resultado
            self.monto_programa_aux = suma

    # METODO PARA SACAR LA FECHA DEL M2M
    @api.one
    @api.depends('programa_contratos')
    def fechaTermino(self):
        for i in self.programa_contratos:
            resultado = str(i.fecha_termino)
            self.fecha_termino_programa = str(resultado)

    @api.one
    @api.depends('monto_programa_aux')
    def DiferenciaPrograma(self):
        self.restante_programa = self.total_partida - self.monto_programa_aux


# CLASE NUEVA
class ProgramaVersion(models.Model):
    _name = 'programa.programa_version'
    _rec_name = 'programa'

    select_tipo = [('1', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:")
    fecha = fields.Date('Fecha:', default=fields.Date.today())
    programa = fields.Many2one('programa.programa_obra', string="Programa:")
    comentario = fields.Text(string="Comentario:", required=False, )


class TablaPrograma(models.Model):
    _name = 'programa.tabla'

    fecha_inicio = fields.Date()
    fecha_termino = fields.Date()
    monto = fields.Float()
