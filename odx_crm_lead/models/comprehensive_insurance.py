from odoo import fields, models, api


class ComprehensiveInsurance(models.Model):
    _name = 'comprehensive.insurance'

    premuium_type_id = fields.Many2one('insurance.premium')
    # vehicle_type = fields.Selection(
    #     [('saloon', 'Saloon'), ('4_4', '4*4'), ('p_up', 'P/UP'), ('motor_cycle', 'Motor Cycle'),
    #      ('trailer_watertanker', 'Trailer & Water Tanker'), ('equipments', 'Equipments'), ('bus', 'Bus'),
    #      ('van', 'Van')],
    #     string="Vehicle Type")
    version_type_id = fields.Many2one('vehicle.version.type',string="Vehicle Type")

    min_year = fields.Float("Min Year")
    max_year = fields.Float("Max Year")
    min_value = fields.Float("Min Value")
    max_value = fields.Float("Max Value")
    premium = fields.Float("Premium Percentage")
    excess_amount = fields.Float("Excess Amount")
    minimum_premium = fields.Float("Minimum Premium")
    repaire_type = fields.Selection(
        [('agency', 'Agency Repair'), ('non_agency', 'Non Agency Repair')], string="Repaire Type")

