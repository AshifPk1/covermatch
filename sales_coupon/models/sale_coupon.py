# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleCouponTemplate(models.Model):
    _name = 'sale.coupon.template'
    _description = 'Sales Coupon Template'

    name = fields.Char('Template Name')
    is_default = fields.Boolean('Default')
    title = fields.Html(string="Title")
    sub_title = fields.Html(string="Sub Title")
    image = fields.Binary(string="Image")
    street_1 = fields.Char(string="Street1")
    street_2 = fields.Char(string="Street2")
    street_3 = fields.Char(string="Street3")
    street_4 = fields.Char(string="Street4")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    phone = fields.Char(string="Phone")
    location_url = fields.Char(string="Location")
    how_to_use = fields.Html(string="How To Use")
    terms_condidion = fields.Html(string="Terms and Condition")


class Couponwizard(models.TransientModel):
    _inherit = "sale.coupon.generate"

    template_id = fields.Many2one('sale.coupon.template', string="Coupon Template")

    def generate_coupon(self):
        """Generates the number of coupons entered in wizard field nbr_coupons
        """
        program = self.env['sale.coupon.program'].browse(self.env.context.get('active_id'))

        vals = {'program_id': program.id}

        if self.generation_type == 'nbr_coupon' and self.nbr_coupons > 0:
            for count in range(0, self.nbr_coupons):
                if self.template_id:
                    vals.update({
                        'title': self.template_id.title or False,
                        'sub_title': self.template_id.sub_title or False,
                        'image': self.template_id.image or False,
                        'street_1': self.template_id.street_1 or False,
                        'street_2': self.template_id.street_2 or False,
                        'street_3': self.template_id.street_3 or False,
                        'street_4': self.template_id.street_4 or False,
                        'country_id': self.template_id.country_id or False,
                        'phone': self.template_id.phone or False,
                        'location_url': self.template_id.location_url or False,
                        'how_to_use': self.template_id.how_to_use or False,
                        'terms_condidion': self.template_id.terms_condidion or False,
                        'template_id': self.template_id.id
                    })
                coupon = self.env['sale.coupon'].create(vals)

        if self.generation_type == 'nbr_customer' and self.partners_domain:
            for partner in self.env['res.partner'].search(safe_eval(self.partners_domain)):
                if self.template_id:
                    vals.update({
                        'title': self.template_id.title or False,
                        'sub_title': self.template_id.sub_title or False,
                        'image': self.template_id.image or False,
                        'street_1': self.template_id.street_1 or False,
                        'street_2': self.template_id.street_2 or False,
                        'street_3': self.template_id.street_3 or False,
                        'street_4': self.template_id.street_4 or False,
                        'country_id': self.template_id.country_id or False,
                        'phone': self.template_id.phone or False,
                        'location_url': self.template_id.location_url or False,
                        'how_to_use': self.template_id.how_to_use or False,
                        'terms_condidion': self.template_id.terms_condidion or False,
                        'template_id': self.template_id.id
                    })
                vals.update({'partner_id': partner.id})
                coupon = self.env['sale.coupon'].create(vals)
                subject = '%s, a coupon has been generated for you' % (partner.name)
                template = self.env.ref('sale_coupon.mail_template_sale_coupon', raise_if_not_found=False)
                if template:
                    template.send_mail(coupon.id, email_values={'email_to': partner.email, 'email_from': self.env.user.email or '', 'subject': subject,})



class SaleOrderCoupon(models.Model):
    _inherit = 'sale.coupon'

    template_id = fields.Many2one('sale.coupon.template', string="Coupon Template")
    title = fields.Html(string="Title")
    sub_title = fields.Html(string="Sub Title")
    image = fields.Binary(string="Image")
    street_1 = fields.Char(string="Street1")
    street_2 = fields.Char(string="Street2")
    street_3 = fields.Char(string="Street3")
    street_4 = fields.Char(string="Street4")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    phone = fields.Char(string="Phone")
    location_url = fields.Char(string="Location")
    how_to_use = fields.Html(string="How To Use")
    terms_condidion = fields.Html(string="Terms and Condition")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reserved', 'Reserved'),
        ('new', 'Valid'),
        ('used', 'Consumed'),
        ('expired', 'Expired')
    ], required=True, default='draft')

    def approve_coupon_action(self):
        for rec in self:
            rec.write({
                'state' : 'new',
            })

    def write(self, vals):
        res = super(SaleOrderCoupon, self).write(vals)
        if vals.get('template_id'):
            template_id = self.env['sale.coupon.template'].browse(vals.get('template_id'))
            self.write({
                        'title': template_id.title or False,
                        'sub_title': template_id.sub_title or False,
                        'image': template_id.image or False,
                        'street_1': template_id.street_1 or False,
                        'street_2': template_id.street_2 or False,
                        'street_3': template_id.street_3 or False,
                        'street_4': template_id.street_4 or False,
                        'country_id': template_id.country_id or False,
                        'phone': template_id.phone or False,
                        'location_url': template_id.location_url or False,
                        'how_to_use': template_id.how_to_use or False,
                        'terms_condidion': template_id.terms_condidion or False,
                    })
        return res


class Program(models.Model):
    _inherit = "sale.coupon.program"

    is_default = fields.Boolean('Default for autmoation')



class SalesOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super(SalesOrder, self)._action_confirm()

        template_id = self.env['sale.coupon.template'].search([('is_default', '=', True)], limit=1)
        program_id = self.env['sale.coupon.program'].search([('is_default', '=', True)], limit=1)
        if template_id and program_id:
            vals = {
                    'title': template_id.title or False,
                    'sub_title': template_id.sub_title or False,
                    'image': template_id.image or False,
                    'street_1': template_id.street_1 or False,
                    'street_2': template_id.street_2 or False,
                    'street_3': template_id.street_3 or False,
                    'street_4': template_id.street_4 or False,
                    'country_id': template_id.country_id or False,
                    'phone': template_id.phone or False,
                    'location_url': template_id.location_url or False,
                    'how_to_use': template_id.how_to_use or False,
                    'terms_condidion': template_id.terms_condidion or False,
                    'partner_id': self.partner_id.id,
                    'program_id': program_id.id,
                    'order_id': self.id
                }
            coupon = self.env['sale.coupon'].create(vals)
            subject = '%s, a coupon has been generated for you' % (self.partner_id.name)
            template = self.env.ref('sale_coupon.mail_template_sale_coupon', raise_if_not_found=False)
            if template:
                template.send_mail(coupon.id, email_values={'email_to': self.partner_id.email, 'email_from': self.env.user.email or '', 'subject': subject,})


