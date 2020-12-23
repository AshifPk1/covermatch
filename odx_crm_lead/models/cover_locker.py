from odoo import fields, models, api


class CoverLocker(models.Model):
    _name = 'cover.locker'

    name = fields.Char('Insurance Name')
    insurance_type = fields.Selection([('thirdparty', 'Third Party'), ('comprehensive', 'Comprehensive')],
                                         string="Insurance Type", required=True)
    insurance_expiry_date = fields.Date('Insurance Expiry Date')
    insurance_premium = fields.Float('Insurance Premium')
    insurance_document = fields.Binary(string='Document', attachment=True)
    insurance_document_name = fields.Char(string='Document Name')

