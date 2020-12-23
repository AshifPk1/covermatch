###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK REST API for Odoo 
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used 
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased 
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the 
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import re
import ast
import json
import urllib
import logging
from xmlrpc import client
import string

from werkzeug import exceptions
import base64
from PIL import Image
import io
from odoo import _, http, release
from odoo.http import request, Response
from odoo.tools import misc, config

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tools.common import parse_value
from odoo.addons.muk_utils.tools.json import ResponseEncoder, RecordEncoder

_logger = logging.getLogger(__name__)
_csrf = config.get('rest_csrf', False)


class ModelController(http.Controller):

    # ----------------------------------------------------------
    # Inspection
    # ----------------------------------------------------------

    @http.route([
        '/api/field_names',
        '/api/field_names/<string:model>',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def field_names(self, model, **kw):
        result = request.env[model].fields_get_keys()
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/fields',
        '/api/fields/<string:model>',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def fields(self, model, fields=None, attributes=None, **kw):
        fields = fields and parse_value(fields) or None
        attributes = attributes and parse_value(attributes) or None
        result = request.env[model].fields_get(allfields=fields, attributes=attributes)
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/metadata',
        '/api/metadata/<string:model>',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def metadata(self, model, ids, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        records = request.env[model].with_context(ctx).browse(ids)
        result = records.get_metadata()
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # ----------------------------------------------------------
    # Search / Read
    # ----------------------------------------------------------

    @http.route([
        '/api/search',
        '/api/search/<string:model>',
        '/api/search/<string:model>/<string:order>',
        '/api/search/<string:model>/<int:limit>/<string:order>',
        '/api/search/<string:model>/<int:limit>/<int:offset>/<string:order>'
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def search(self, model, domain=None, context=None, count=False, limit=80, offset=0, order=None, **kw):
        ctx = request.session.context.copy()
        ctx.update({'prefetch_fields': False})
        ctx.update(context and parse_value(context) or {})
        domain = domain and parse_value(domain) or []
        count = count and misc.str2bool(count) or None
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        model = request.env[model].with_context(ctx)
        result = model.search(domain, offset=offset, limit=limit, order=order, count=count)
        if not count:
            result = result.ids
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/name',
        '/api/name/<string:model>',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def name(self, model, ids, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        records = request.env[model].with_context(ctx).browse(ids)
        result = records.name_get()
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/read',
        '/api/read/<string:model>',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def read(self, model, ids, fields=None, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        fields = fields and parse_value(fields) or None
        records = request.env[model].with_context(ctx).browse(ids)
        result = records.read(fields=fields)
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/search_read',
        '/api/search_read/<string:model>',
        '/api/search_read/<string:model>/<string:order>',
        '/api/search_read/<string:model>/<int:limit>/<string:order>',
        '/api/search_read/<string:model>/<int:limit>/<int:offset>/<string:order>'
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def search_read(self, model, domain=None, fields=None, context=None, limit=80, offset=0, order=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        domain = domain and parse_value(domain) or []
        fields = fields and parse_value(fields) or None
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        model = request.env[model].with_context(ctx)
        result = model.search_read(domain, fields=fields, offset=offset, limit=limit, order=order)
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/read_group',
        '/api/read_group/<string:model>',
        '/api/read_group/<string:model>/<string:orderby>',
        '/api/read_group/<string:model>/<int:limit>/<string:orderby>',
        '/api/read_group/<string:model>/<int:limit>/<int:offset>/<string:orderby>'
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def read_group(self, model, domain, fields, groupby, context=None, offset=0, limit=None, orderby=False, lazy=True,
                   **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        domain = domain and parse_value(domain) or []
        fields = fields and parse_value(fields) or []
        groupby = groupby and parse_value(groupby) or []
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        lazy = misc.str2bool(lazy)
        model = request.env[model].with_context(ctx)
        result = model.read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    # ----------------------------------------------------------
    # Create / Update / Delete
    # ----------------------------------------------------------

    @http.route([
        '/api/create',
        '/api/create/<string:model>',
    ], auth="none", type='http', methods=['POST'], csrf=_csrf)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected(operations=['create'])
    def create(self, model, values=None, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        values = values and parse_value(values) or {}
        model = request.env[model].with_context(ctx)
        result = model.create(values).ids
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/write',
        '/api/write/<string:model>',
    ], auth="none", type='http', methods=['PUT'], csrf=_csrf)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected(operations=['write'])
    def write(self, model, ids=None, values=None, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        values = values and parse_value(values) or {}
        records = request.env[model].with_context(ctx).browse(ids)
        result = records.write(values)
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/unlink',
        '/api/unlink/<string:model>',
    ], auth="none", type='http', methods=['DELETE'], csrf=_csrf)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected(operations=['unlink'])
    def unlink(self, model, ids=None, context=None, **kw):
        ctx = request.session.context.copy()
        ctx.update(context and parse_value(context) or {})
        ids = ids and parse_value(ids) or []
        records = request.env[model].with_context(ctx).browse(ids)
        result = records.unlink()
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/get-premiums',
    ], auth="none", type='http', methods=['GET'])
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    @tools.security.protected()
    def premiums(self, **kw):
        product_type = kw.get('product_type')
        agency_repair = kw.get('agency_repair')
        takaful = kw.get('takaful')
        car_data = kw.get('car_data')
        car_value = kw.get('car_value')
        vehicle_id = kw.get('vehicle_id')
        driver_age = kw.get('driver_age')
        domain = []
        vehicle_type = ''

        if takaful == "True":
            takaful = True
        if takaful == "False":
            takaful = False
        vehicles = ''
        if vehicle_id:
            vehicles = request.env['uae.car.valuation'].sudo().search([('id', '=', vehicle_id)])
            if vehicles:
                vehicle_type = vehicles.version_type_id
                if int(vehicles.no_of_cylinder) == 4:
                    cyl = '4cyl'
                if int(vehicles.no_of_cylinder) == 6:
                    cyl = '6cyl'
                if int(vehicles.no_of_cylinder) == 8:
                    cyl = '8cyl'
                if int(vehicles.no_of_cylinder) == 12:
                    cyl = '12cyl'

        if product_type == 'comprehensive':
            domain.append(('insurance_premium', '=', product_type))
            if vehicles:
                domain.append(('comprehensive_insurance_ids.version_type_id', '=', vehicle_type.id))

        elif product_type == 'thirdparty':
            domain.append(('insurance_premium', '=', product_type))
            if vehicles:
                domain.append(('third_party_insurance_ids.version_type_id', '=', vehicle_type.id))
        else:
            if vehicles:
                domain.append('|')
                domain.append(('comprehensive_insurance_ids.version_type_id', '=', vehicle_type.id))
                domain.append(('third_party_insurance_ids.version_type_id', '=', vehicle_type.id))

        if kw.get('takaful'):
            domain.append(('insurance_company_id.is_takaful', '=', takaful))
        if kw.get('agency_repair'):
            domain.append(('repaire_type', '=', agency_repair))
        if kw.get('driver_age'):
            domain.append(('driver_aged', '<=', driver_age))
            domain.append(('driver_aged_max', '>=', driver_age))

        insurance_policy = request.env['insurance.premium'].sudo().search(domain)
        # if not domain:
        #     result = {'message': 'No matching Polcy Found!'}
        #     content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        #     return Response(content, content_type='application/json;charset=utf-8', status=200)
        result = []
        for policy in insurance_policy:
            if vehicles in policy.included_vehicle_ids:
                continue
            benefits = []
            insurance = []

            insurance_company = {'name': policy.insurance_company_id.name,
                                 'image': policy.insurance_company_id.image_1920,
                                 'street': policy.insurance_company_id.street,
                                 'street2': policy.insurance_company_id.street2,
                                 'city': policy.insurance_company_id.city,
                                 'takaful': policy.insurance_company_id.is_takaful,
                                 'state': policy.insurance_company_id.state_id.name if policy.insurance_company_id.state_id else '',
                                 'country': policy.insurance_company_id.country_id.name if policy.insurance_company_id.country_id else '',
                                 'zip': policy.insurance_company_id.zip,
                                 'phone': policy.insurance_company_id.phone,
                                 'website': policy.insurance_company_id.website
                                 }
            if product_type == 'comprehensive':
                for comphrensive in policy.comprehensive_insurance_ids:
                    if comphrensive.version_type_id == vehicle_type and comphrensive.min_value <= vehicles.estimated_price_new_min and comphrensive.max_value >= vehicles.estimated_price_new_max:
                        comphrensive_dict = {
                            'product_type': 'comprehensive',
                            'vehicle_type': comphrensive.version_type_id.name,
                            'min_year': comphrensive.min_year,
                            'max_year': comphrensive.max_year,
                            'min_value': comphrensive.min_value,
                            'max_value': comphrensive.max_value,
                            'premium_percentage': comphrensive.premium,
                            'excess_amount': comphrensive.excess_amount,
                            'minimum_premium': comphrensive.minimum_premium
                        }
                        insurance.append(comphrensive_dict)

            elif product_type == 'thirdparty':
                for third_party in policy.third_party_insurance_ids:
                    if third_party.version_type_id == vehicle_type and third_party.no_of_cylinder == cyl:
                        third_party_dict = {
                            'product_type': 'thirdparty',
                            'no_of_cylinder': third_party.no_of_cylinder,
                            'premium': third_party.premium,

                        }
                        insurance.append(third_party_dict)
            else:
                for comphrensive in policy.comprehensive_insurance_ids:
                    if comphrensive.version_type_id == vehicle_type and comphrensive.min_value <= vehicles.estimated_price_new_min and comphrensive.max_value >= vehicles.estimated_price_new_max:
                        comphrensive_dict = {
                            'product_type': 'comprehensive',
                            'vehicle_type': comphrensive.version_type_id.name,
                            'min_year': comphrensive.min_year,
                            'max_year': comphrensive.max_year,
                            'min_value': comphrensive.min_value,
                            'max_value': comphrensive.max_value,
                            'premium_percentage': comphrensive.premium,
                            'excess_amount': comphrensive.excess_amount,
                            'minimum_premium': comphrensive.minimum_premium
                        }
                        insurance.append(comphrensive_dict)

                for third_party in policy.third_party_insurance_ids:
                    if third_party.version_type_id == vehicle_type and third_party.no_of_cylinder == cyl:
                        third_party_dict = {
                            'vehicle_type': third_party.version_type_id.name,
                            'product_type': 'thirdparty',
                            'no_of_cylinder': third_party.no_of_cylinder,
                            'premium': third_party.premium,

                        }
                        insurance.append(third_party_dict)

            for include in policy.included_ids:
                exclude_benefit_dict = {
                    'name': include.name,
                    'primary': include.primary_benefit,
                    'benefit_type': 'included',
                    'tooltip_message': include.help_note
                }
                benefits.append(exclude_benefit_dict)
            for exclude in policy.excluded_ids:
                include_benefit_dict = {
                    'name': exclude.name,
                    'primary': exclude.primary_benefit,
                    'benefit_type': 'exclude',
                    'tooltip_message': exclude.help_note
                }
                benefits.append(include_benefit_dict)
            for optional in policy.optional_ids:
                optional_benefit_dict = {
                    'name': optional.name,
                    'primary': optional.primary_benefit,
                    'benefit_type': 'optional',
                    'price': optional.additional_premium,
                    'tooltip_message': optional.help_note
                }
                benefits.append(optional_benefit_dict)
            no_claim_discount = {
                '1year': policy.year1,
                '2year': policy.year2,
                '3year': policy.year3
            }
            policy_dict = {
                'insurance_company': insurance_company,
                'insurance': insurance,
                'policy_name': policy.name,
                'benefits': benefits,
                'brokarage': policy.brokarage,
                'no_claim_discount': no_claim_discount

            }
            result.append(policy_dict)
        if not result:
            result = {'message': 'No matching Polcy Found!'}
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/sale/confirm/<string:id>',
    ], auth="none", type='http', methods=['POST'], csrf=_csrf)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    def confirm_sale_irder(self, id, **kw, ):
        sale_order = request.env['sale.order'].sudo().search(
            [('id', '=', id)], limit=1)
        if sale_order:
            sale_order.action_confirm()
            result = {
                'message': "Sale Order Confirmed",
            }
        else:
            result = {
                'message': "Cannot find the sale order ",
            }
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)

    @http.route([
        '/api/sale/email/<string:id>',
    ], auth="none", type='http', methods=['POST'], csrf=_csrf)
    @tools.common.parse_exception
    @tools.common.ensure_database
    @tools.common.ensure_module()
    def send_sale_email(self, id, **kw, ):
        sale_order = request.env['sale.order'].sudo().search(
            [('id', '=', id)], limit=1)

        ir_model_data = request.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'mail_template_sale_confirmation')[1]
        except ValueError:
            template_id = False
        pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([int(id)])
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = "Sale Order"
        attachment_id = request.env['ir.attachment'].sudo().create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': 'sale.order',
            'res_id': id,
            'mimetype': 'application/x-pdf'
        })
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': id,
            'default_use_template': True,
            'default_template_id': template_id,
            'web_base_url': request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'force_email': True,
        }
        template = request.env['mail.template'].sudo().browse(template_id)
        html_body = template.body_html
        text = template.with_context(ctx)._render_template(html_body, 'sale.order', int(id))
        compose = request.env['mail.mail'].sudo().create({
            'subject': 'Sale Order',
            'email_from': request.env.user.email,
            'email_to': sale_order.partner_id.email,
            'body_html': text,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,
        })
        compose.send()

        if compose and sale_order:
            result = {
                'message': "Succesfully Send Email",
            }
        else:
            result = {
                'message': "Cannot find the sale order ",
            }
        content = json.dumps(result, sort_keys=True, indent=4, cls=ResponseEncoder)
        return Response(content, content_type='application/json;charset=utf-8', status=200)


