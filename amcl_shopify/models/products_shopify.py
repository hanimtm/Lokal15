# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import pprint
import re
from ..shopify.utils import *
from odoo import models, api, fields, tools, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_id = fields.Char(string="Shopify Id", store=True, copy=False)
    marketplace_type = fields.Selection(selection_add=[('shopify', 'Shopify')])
    shopify_categ_ids = fields.One2many('shopify.product.category',
                                        'product_tmpl_id',
                                        string="Shopify Categories",
                                        readonly=True)
    shopify_type = fields.Char(string="Shopify Product Type",
                               readonly=True, store=True)
    custom_option = fields.Boolean(string="Custom Option", default=False)
    # New Fields
    shopify_published_scope = fields.Char()
    shopify_tags = fields.Char()
    shopify_template_suffix = fields.Char()
    shopify_variants = fields.Char()
    # shopify_vendor = fields.Char()
    shopify_vendor = fields.Many2one('res.partner','Vendor')
    # Fields for Shopify Products
    shopify_compare_price = fields.Monetary(string='Compare at price')
    shopify_charge_tax = fields.Boolean(string='Charge tax?')
    shopify_track_qty = fields.Boolean(string='Track quantity?')
    shopify_product_status = fields.Selection(
        string='Product status',
        selection=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')],
        default='active',
    )
    shopify_collections = fields.Char()

    def _compute_shopify_vendor(self):
        for product in self:
            product.shopify_vendor = product.env['product.product'].search\
                ([('product_tmpl_id','=',product.id)],limit=1).shopify_vendor.id

    def action_create_shopify_product(self):
        data = get_protmpl_vals(self, {})
        _logger.info("data ===>>>", data)
        shopify_pt_request(self, data, 'create')

    def shopify_create_product(self, result, values):
        if not values.get('shopify_id') and result.marketplace_type == 'shopify':
            data = get_protmpl_vals(result, values)
            shopify_pt_request(self, data, 'create')

    def action_update_shopify_product(self):
        data = get_protmpl_vals(self, {"req_type":'update'})
        res = shopify_pt_request(self, data, 'update')

    # @api.model
    # def create(self, values):
    #     print(values)
    #     if values.get('shopify_id'):
    #         ProTmpl = self.env['product.template'].sudo()
    #         product = ProTmpl.search(
    #             [('shopify_id', '=', values.get('shopify_id'))], limit=1)
    #         if product:
    #             _logger.warning(
    #                 "Product already exists with id=%s and shopify id = %s", product.id, product.shopify_id)
    #             return product.id
    #         else:
    #             result = super(ProductTemplate, self).create(values)
    #     else:
    #         result = super(ProductTemplate, self).create(values)

    #     self.shopify_create_product(result, values)
    #     return result


class ProductProductShopify(models.Model):
    _inherit = 'product.product'

    marketplace_type = fields.Selection(selection_add=[('shopify', 'Shopify')])
    shopify_categ_ids = fields.One2many('shopify.product.category',
                                        'product_id',
                                        string="Shopify Categories",
                                        readonly=True)

    shopify_id = fields.Char(string="Shopify Id",
                             store=True, copy=False)
    shopify_type = fields.Char(string="Shopify Type",
                               readonly=True, store=True)
    shopify_com = fields.Char(string='shopify_com', )
    shopify_image_id = fields.Char(string="Shopify Image Id",
                                  store=True, copy=False)

    @api.depends('product_template_attribute_value_ids','product_tmpl_id')
    def _compute_shopify_vendor(self):
        for product in self:
            product.shopify_vendor = product.product_tmpl_id.shopify_vendor.id

    @api.depends('product_template_attribute_value_ids')
    def _compute_combination_indices(self):
        for product in self:
            product.combination_indices = product.product_template_attribute_value_ids._ids2str()
            if product.product_template_attribute_value_ids._ids2str() == '' and product.marketplace_type == 'shopify':
                product.combination_indices = product.shopify_com

    compare_at_price = fields.Char(string='compare_at_price', )
    fulfillment_service = fields.Char(string='fulfillment_service', )
    inventory_management = fields.Char(string='inventory_management', )
    inventory_policy = fields.Char(string='inventory_policy', )
    requires_shipping = fields.Boolean(
        string='requires_shipping',
    )
    taxable = fields.Boolean(
        string='taxable',
    )

    # shopify_vendor = fields.Char()
    shopify_vendor = fields.Many2one('res.partner','Vendor',compute='_compute_shopify_vendor')
    shopify_collections = fields.Char()

    def action_create_shopify_product(self):
        data = get_protmpl_vals(self, {})
        _logger.info("data ===>>>", data)
        shopify_pt_request(self, data, 'create')

    def action_update_shopify_product(self):
        data = get_protmpl_vals(self, {})
        res = shopify_pt_request(self, data, 'update')
        print("RES====>>>>", res)

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record

            @return: returns ProductTemplateShopify id of new record
        """
        result = super(ProductProductShopify, self).create(values)
        if values.get('product_tmpl_id'):
            """Create a Products"""
            product_tmpl_id = self.env['product.template'].sudo().search([('id', '=', values.get('product_tmpl_id'))],
                                                                         limit=1)
            values['marketplace_type'] = product_tmpl_id.marketplace_type if product_tmpl_id.marketplace_type else None
        ######################################################################################################################
        # if values.get('shopify_id'):
        #     ProTmpl = self.env['product.product'].sudo()
        #     product = ProTmpl.search(
        #         [('shopify_id', '=', values.get('shopify_id'))], limit=1)
        #     if product:
        #         _logger.warning(
        #             "Product already exists with id=%s and shopify id = %s", product.id, product.shopify_id)
        #         return product.id
        #     else:
        #         result = super(ProductProductShopify, self).create(values)

        # else:
        #     result = super(ProductProductShopify, self).create(values)
        ######################################################################################################################
        return result


class ProductCategshopify(models.Model):
    _inherit = 'product.category'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )
    shopify_id = fields.Integer(string="shopify id of the category",
                                readonly=True,
                                store=True)


class ShopifyCategory(models.Model):
    _name = 'shopify.product.category'
    _description = 'shopify Product Category'
    _rec_name = 'categ_name'

    name = fields.Many2one('product.category', string="Category")
    categ_name = fields.Char(string="Actual Name")
    product_tmpl_id = fields.Many2one(
        'product.template', string="Product Template Id")
    product_id = fields.Many2one('product.product', string="Product")


class ProductAttributeValueExtended(models.Model):
    _inherit = 'product.attribute.value'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )


# class ProductAttributeSet(models.Model):
#     _name = 'product.attribute.set'
#     _description = 'Product Attribute Set'

#     marketplace_type = fields.Selection(
#         selection_add=[('shopify', 'Shopify')]
#     )

#     name = fields.Char('Attribute Set')
#     code = fields.Char('Code')
#     attribute_rel = fields.One2many(
#         'product.attribute', 'attribute_set', string="Attributes")


class ProductAttributeExtended(models.Model):
    _inherit = 'product.attribute'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )
    attribute_set_id = fields.Integer(string="Ids")
    # attribute_set = fields.Many2one('product.attribute.set')


# class ProductImaget(models.Model):
#     _inherit = 'product.image'

#     marketplace_type = fields.Selection([], string="Marketplace Type")

class ProductAttributeExtended(models.Model):
    _inherit = 'product.attribute'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )


class ProductAttributeValueExtended(models.Model):
    _inherit = 'product.attribute.value'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )


class PTAL(models.Model):
    _inherit = 'product.template.attribute.line'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )


class SCPQ(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    marketplace_type = fields.Selection(
        selection_add=[('shopify', 'Shopify')]
    )
