# -*- coding: utf-8 -*-
{
    'name': "Base Marketplace",
    'version': '15.0.1.0.0',
    'summary': """Base Module for Marketplace""",
    'description': """Base Module for Marketplace""",
    'category': 'Extra Tools',
    'author': "amcl Inc.",
    'website': "https://www.amcl.com",
    'company': 'AMCL',
    'maintainer': 'AMCL',
    'depends': ['base','stock','mail'],
    'external_dependencies': {'python': []},
    'images': [
        'static/description/banner.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/instance_view.xml',
        # 'views/sync_history.xml',
        'data/ir_sequence_data.xml',
        'wizard/update_stock.xml',
        # 'wizard/fetch_customers_wiz.xml',
        # 'data/ir_cron_data.xml',
    ],
    'price': 0,
    'currency': 'USD',
    'license': 'OPL-1',
    'support': "support@amcl.com",
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'uninstall_hook': 'uninstall_hook',
}