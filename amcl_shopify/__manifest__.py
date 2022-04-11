# -*- coding: utf-8 -*-
{
    'name': "Odoo Shopify Connector",
    'summary': """Odoo Shopify Connector""",
    'description': """Odoo Shopify Connector""",
    'author': "amcl Inc",
    'website': "http://www.amcl.com",
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',
    'depends': ['base', 'mail', 'amcl_base_marketplace', 'sale','sale_management', 'stock','sale_stock','delivery','product'],
    'images': [
        'static/description/banner.gif',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/product_template.xml',
        'views/marketplace_instance.xml',
        'views/sale_order.xml',
        'views/account.xml',
        'views/stock.xml',
        # Wizards
        'wizard/fetch_customers_wiz.xml',
        'wizard/fetch_orders_wiz.xml',
        'wizard/fetch_products_wiz.xml',
        'wizard/update_stock.xml',
        'wizard/customer_delete_wiz.xml',
        'views/webhooks.xml',
        # Data
        'data/ir_cron_data.xml',
        'data/update_history.xml',
        'data/product.xml',
    ],
    'price': 500,
    'currency': 'USD',
    'license': 'OPL-1',
    'support': "support@amcl.com"

}
