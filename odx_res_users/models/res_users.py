# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_type = fields.Char(string="Login Type",help="email, facebook, google")
