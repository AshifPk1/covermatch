# -*- coding: utf-8 -*-
{
    'name': "CRM Facebook Lead Ads",

    'summary': """
        Sync Facebook Leads with Odoo CRM""",

    'description': """
    """,

    'author': "Odox Softhub",
    'website': "http://odoxsofthub.com",

    'category': 'Lead Automation',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm','odx_crm_lead'],
    'images': ['static/src/img/banner.png'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_view.xml',
    ]
}
