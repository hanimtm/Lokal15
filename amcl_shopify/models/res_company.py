# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    global_commission = fields.Float('Global Commission')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_commission = fields.Float(string="Global Commission", default=lambda self: self.env.user.company_id.global_commission, related="company_id.global_commission", readonly=False)