from odoo import fields, models, api


class ThirdPartyInsurance(models.Model):
    _name = 'thirdparty.insurance'

    premuium_type_id = fields.Many2one('insurance.premium')
    # vehicle_type = fields.Selection(
    #     [('saloon', 'Saloon'), ('4_4', '4*4'), ('p_up', 'P/UP'), ('motor_cycle', 'Motor Cycle'),
    #      ('trailer_watertanker', 'Trailer & Water Tanker'), ('equipments', 'Equipments'), ('bus', 'Bus'),
    #      ('van', 'Van')],
    #     string="Vehicle Type")
    version_type_id = fields.Many2one('vehicle.version.type', string="Vehicle Type")
    no_of_cylinder = fields.Selection(
        [('4cyl', '4Cyl'),('6cyl', '6Cyl'),('8cyl', '8Cyl'),('12cyl', '12Cyl')],string="No Of Cylinders")

    premium = fields.Float("Premium")
