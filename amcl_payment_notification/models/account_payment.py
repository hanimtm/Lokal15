# -*- coding: utf-8 -*-


from odoo import models, fields
from odoo.http import request


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    transfer_attachment = fields.Binary(attachment=True)

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'transfer_attachment': self.transfer_attachment
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals


class AccountPayment(models.Model):
    _inherit = "account.payment"


    transfer_attachment = fields.Binary(attachment=True)

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        template_id = self.env.ref('amcl_payment_notification.invoice_payment_transferred')
        if template_id:
            for payment in self:
                if payment.payment_type == 'outbound':

                    if self.transfer_attachment:
                        attachment = {
                            'name': 'Bank Transfer Document',
                            'datas': self.transfer_attachment,
                            'res_model': 'account.payment',
                            'type': 'binary'
                        }
                        ir_id = self.env['ir.attachment'].create(attachment)
                        template_id.attachment_ids = [(4, ir_id.id)]
                        template_id.send_mail(payment.id)
        return res
