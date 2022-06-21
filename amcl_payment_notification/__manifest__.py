# -*- coding: utf-8 -*-

{
    'name': "Invoice Transferred Mail",
    'summary': "Send email when invoice payment is transferred",
    'description': "Send email when invoice payment is transferred",
    'version': "1.0",
    'category': "Accounting/Accounting",
    'author': "Aneesh",
    'license': 'LGPL-3',
    'depends': [
        'account'
    ],
    'data': [
        'data/email.xml',
        'views/account_payment.xml',
        'views/res_config.xml',
    ],
    'application': False,
    'installable': True,
}
