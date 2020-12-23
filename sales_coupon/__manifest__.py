# -*- coding: utf-8 -*-
{
    'name': "Odoo Sales Coupon",  # Name first, others listed in alphabetical order
    'application': False,
    'author': "Nikunj Dhameliya",
    'auto_install': False,
    'category': "Extra Tools",  # Odoo Marketplace category
    'data': [  # Files are processed in the order of listing
        'report/report_paperformat.xml',
        'security/ir.model.access.csv',
        'security/coupon_security.xml',
        'report/sale_coupon_report.xml',
        'report/sale_coupon_report_templates.xml',
        'views/sales_coupon.xml',
    ],
    'demo': [],
    'depends': [  # Include only direct dependencies
        'sale', 'website_sale_coupon', 'sale_coupon'
    ],
    'qweb': [
     ],
    'description': "Odoo Sales Coupon",
    'installable': True,
    'summary': "Odoo Sales Coupon",
    'test': [],
    'version': "1.0.1",
    'website': "https://www.fiverr.com/nikunjd",
}
