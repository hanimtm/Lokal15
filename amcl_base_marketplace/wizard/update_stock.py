# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################


from odoo import models, fields, exceptions, _, api
import logging
import re

logger = logging.getLogger(__name__)


class ProductsFetchWizard(models.Model):
    _name = 'update.stock.wizard'
    _description = 'Stock Update Wizard'

    fetch_type = fields.Selection([
        ('to_odoo', 'Import stock status'),
        ('from_odoo', 'Export stock status')
    ], string="Operation Type")

    
    @api.onchange('fetch_type')
    def _onchange_field(self):
        print("_onchange_field")
    
    def update_stock_item(self):
        print("******update_stock_item")
        ICPSudo = self.env['ir.config_parameter'].sudo()
        try:
            marketplace_instance_id = ICPSudo.get_param('amcl_base_marketplace.marketplace_instance_id')
            marketplace_instance_id = [int(s) for s in re.findall(r'\b\d+\b', marketplace_instance_id)]
        except:
            marketplace_instance_id = False
        if marketplace_instance_id:
            marketplace_instance_id = self.env['marketplace.instance'].sudo().search([('id','=',marketplace_instance_id[0])])
            kwargs = {'marketplace_instance_id': marketplace_instance_id}
            if hasattr(self, '%s_update_stock_item' % marketplace_instance_id.marketplace_instance_type):
                return getattr(self, '%s_update_stock_item' % marketplace_instance_id.marketplace_instance_type)(kwargs)

