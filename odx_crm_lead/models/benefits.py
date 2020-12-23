from odoo import fields, models, api


class Benefits(models.Model):
    _name = 'res.benefits'
    _rec_name = 'display_name'

    name = fields.Char("Name", required=True)
    # excess_amount = fields.Float("Excess Amount")
    help_note = fields.Text("Help")
    is_optional = fields.Boolean("Is Optional")
    is_included = fields.Boolean("Is Included")
    is_excluded = fields.Boolean("Is Excluded")
    primary_benefit = fields.Boolean("Primary Benefit")
    additional_premium = fields.Float("Additional Premium")
    display_name = fields.Char(compute="_compute_display_name")
    product_id = fields.Many2one('product.product', "Benefit Product", required=True)

    @api.depends('name','additional_premium')
    def _compute_display_name(self):
        for record in self:
            if record.additional_premium:
                record.display_name = '%s-%s' % (record.name,record.additional_premium)
            else:
                record.display_name = '%s' % (record.name)
