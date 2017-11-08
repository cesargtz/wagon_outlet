# -*- coding: utf-8 -*-

from odoo import api, fields, models


class WagonOutlet(models.Model):
    _inherit = ['wagon', 'vehicle.outlet', 'mail.thread']
    _name = 'wagon.outlet'

    state = fields.Selection([
        ('capture', 'Capturar'),
        ('load', 'Cargar'),
        ('analysis', 'Analisis'),
        ('done', 'Hecho'),
    ], default='capture')

   #_defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code_wo'), }
    name = fields.Char('wagon outlet reference', required=True, select=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('reg_code_wo'), help="Unique number of the wagon outlet")
    
    @api.one
    @api.depends('contract_id')
    def _compute_product_id(self):
        product_id = False
        for line in self.contract_id.order_line:
            product_id = line.product_id.id
            break
        self.product_id = product_id

    @api.one
    @api.depends('contract_id', 'raw_kilos')
    def _compute_delivered(self):
        self.delivered = sum(record.raw_kilos for record in self.contract_id.wagon_outlet_ids) / 1000

    @api.one
    def fun_load(self):
        self.state = 'analysis'

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'capture':
                self.write({'state': 'load'}, 'r')
            elif self.state == 'load':
                self.write({'state': 'analysis'}, 'r')
            elif self.state == 'analysis':
                self.write({'state': 'done'}, 'r')

        res = super(WagonOutlet, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'load'
        res = super(WagonOutlet, self).create(vals)
        return res
