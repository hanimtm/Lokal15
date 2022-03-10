# -*- coding: utf-8 -*-
###############################################################################
from odoo import models, fields, exceptions, api, _
import logging
from itertools import groupby
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

logger = logging.getLogger(__name__)


class SaleOrderShopify(models.Model):
    _inherit = 'sale.order'

    shopify_id = fields.Char(string="Shopify Id", readonly=True,
                             store=True)
    shopify_order = fields.Char(string="Shopify Order", readonly=True,
                             store=True)

    marketplace_type = fields.Selection(
        [('shopify', 'Shopify')], string="Marketplace Type"
    )
    shopify_status = fields.Char(string="shopify status", readonly=True)
    shopify_order_date = fields.Datetime(string="shopify Order Date")
    shopify_carrier_service = fields.Char(string="shopify Carrier Service")
    shopify_has_delivery = fields.Boolean(
        string="shopify has delivery", readonly=True, default=False, compute='shopifyhasdelviery')
    shopify_browser_ip = fields.Char(string='Browser IP',)
    shopify_buyer_accepts_marketing = fields.Boolean(
        string='Buyer Merketing',
    )
    shopify_cancel_reason = fields.Char(
        string='Cancel Reason',
    )
    shopify_cancelled_at = fields.Datetime(
        string='Cancel At',
    )
    shopify_cart_token = fields.Char(
        string='Cart Token',
    )
    shopify_checkout_token = fields.Char(
        string='Checkout Token',
    )
    shopify_currency = fields.Many2one(
        string='Shop Currency',
        comodel_name='res.currency',
        ondelete='restrict',
    )
    shopify_financial_status = fields.Selection(
        string='Financial Status',
        selection=[('pending', 'Pending'),
                   ('authorized', 'Authorized'),
                   ('partially_paid', 'Partially Paid'),
                   ('paid', 'Paid'),
                   ('partially_refunded', 'Partially Refunded'),
                   ('voided', 'Voided')
                   ], default='pending'

    )
    shopify_fulfillment_status = fields.Char(
        string='Fullfillment Status',
    )
    shopify_track_updated = fields.Boolean(
        string='Shopify Track Updated',
        default=False,
        readonly=True,
    )

    def _create_invoices_new(self, mkplc_id, grouped=False, final=False, date=None):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        invoice_vals_list = []
        invoice_item_sequence = 0

        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            invoice_vals = order._prepare_invoice()
            invoice_vals['move_type'] = 'out_invoice'
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                # if not down_payment_section_added and line.is_downpayment:
                #     invoice_line_vals.append(
                #         (0, 0, order._prepare_down_payment_section_line(
                #             sequence=invoice_item_sequence,
                #         )),
                #     )
                #     down_payment_section_added = True
                #     invoice_item_sequence += 1
                debit = mkplc_id.debit_account_id
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line_new(
                        sequence=invoice_item_sequence,debit=debit
                    )),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        print('invoice_vals_list ** :: ',invoice_vals_list)
        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        # if not grouped:
        #     new_invoice_vals_list = []
        #     invoice_grouping_keys = self._get_invoice_grouping_keys()
        #     invoice_vals_list = sorted(
        #         invoice_vals_list,
        #         key=lambda x: [
        #             x.get(grouping_key) for grouping_key in invoice_grouping_keys
        #         ]
        #     )
        #     for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
        #         origins = set()
        #         payment_refs = set()
        #         refs = set()
        #         ref_invoice_vals = None
        #         for invoice_vals in invoices:
        #             if not ref_invoice_vals:
        #                 ref_invoice_vals = invoice_vals
        #             else:
        #                 ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
        #             origins.add(invoice_vals['invoice_origin'])
        #             payment_refs.add(invoice_vals['payment_reference'])
        #             refs.add(invoice_vals['ref'])
        #         ref_invoice_vals.update({
        #             'ref': ', '.join(refs)[:2000],
        #             'invoice_origin': ', '.join(origins),
        #             'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
        #         })
        #         new_invoice_vals_list.append(ref_invoice_vals)
        #     invoice_vals_list = new_invoice_vals_list

        # if len(invoice_vals_list) < len(self):
        #     SaleOrderLine = self.env['sale.order.line']
        #     for invoice in invoice_vals_list:
        #         sequence = 1
        #         for line in invoice['invoice_line_ids']:
        #             line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
        #             sequence += 1
        # moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        print('Final Invocie line :: ' , invoice_vals_list)

        moves = self.env['account.move'].sudo().with_company(self.env.company.id).create(invoice_vals_list)
        print('Final moves :: ', moves)
        # if final:
        #     moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        # for move in moves:
        #     move.message_post_with_view('mail.message_origin_link',
        #         values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
        #         subtype_id=self.env.ref('mail.mt_note').id
        #     )
        return moves

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shopify_id = fields.Char(string="Shopify Id", readonly=True,
                             store=True)
    marketplace_type = fields.Selection(
        [('shopify', 'Shopify')], string="Marketplace Type"
    )
    shopify_vendor = fields.Many2one(related='product_id.shopify_vendor')

    def _prepare_invoice_line_new(self, debit, **optional_values):
        self.ensure_one()
        res = {
                'display_type': self.display_type,
                'sequence': self.sequence,
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'discount': self.discount,
                'price_unit': self.price_unit,
                'tax_ids': [(6, 0, self.tax_id.ids)],
                'analytic_account_id': self.order_id.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'sale_line_ids': [(4, self.id)],
                'account_id': self.product_id.property_account_income_id.id or \
                              self.product_id.categ_id.property_account_income_categ_id.id or \
                              debit.id or False
            }
        if optional_values:
             res.update(optional_values)
        return res
