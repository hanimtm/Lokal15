# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# class addson/account_parent(models.Model):
#     _name = 'addson/account_parent.addson/account_parent'
#     _description = 'addson/account_parent.addson/account_parent'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
class AccountGroup(models.Model):
    _inherit = 'account.group'

    @api.constrains('code_prefix_start', 'code_prefix_end')
    def _constraint_prefix_overlap(self):
        self.env['account.group'].flush()
        query = """
                SELECT other.id FROM account_group this
                JOIN account_group other
                  ON char_length(other.code_prefix_start) = char_length(this.code_prefix_start)
                 AND other.id != this.id
                 AND other.company_id = this.company_id
                 AND (
                    other.code_prefix_start <= this.code_prefix_start AND this.code_prefix_start <= other.code_prefix_end
                    OR
                    other.code_prefix_start >= this.code_prefix_start AND this.code_prefix_end >= other.code_prefix_start
                )
                WHERE this.id IN %(ids)s
            """
        self.env.cr.execute(query, {'ids': tuple(self.ids)})
        res = self.env.cr.fetchall()
        # if res:
        #     raise ValidationError(_('Account Groups with the same granularity can\'t overlap'))