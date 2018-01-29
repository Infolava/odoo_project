# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2018 Infolava GmbH. All rights reserved.
# License:
# --------------------------------------------------------------------------------
#    This file is part of TransALM
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# --------------------------------------------------------------------------------
# Created:               Jan 24, 2018 10:34:32 AM by atrabelsi
# Last modified:      2018-01-24 10:34
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _ 
from openerp.exceptions import ValidationError
from openerp.osv import expression
from openerp.tools.safe_eval import safe_eval
from lxml import etree

class ir_field_rule(models.Model):
    _name = "ir.field.rule"
    _description = "Define a set of domain to field access according to user group"
    
    name = fields.Text("Field Domain Name", required = True)
    domain_force = fields.Text("Domain", required = True)
    group_ids = fields.Many2many("res.groups", string = "Groups", required = True)
    model_id = fields.Many2one("ir.model", "Model", required = True)
    active = fields.Boolean('Active', default = True)
    field_id = fields.Many2one("ir.model.fields", "Field", required = True,)
    
    @api.constrains('model_id')
    def _check_field_model(self):
        if self.field_id and self.field_id.model_id != self.model_id :
            raise ValidationError(_("Specified field must belong to the model %s" %self.model_id.name))
        
    @api.model
    def compute_domain(self, field_name, model_name):
        field_id = self.env['ir.model.fields'].search([('name', '=', field_name), ('model_id.model', '=', model_name)]).id
        field_rules = self
        group_domain = []
        group_domains = {}
        if field_id : 
            for gp in self.env.user.groups_id :
                field_rules = field_rules | self.search([('field_id', '=', field_id), \
                                                         ('active', '=', True), \
                                                         ('group_ids', 'in', gp.ids),
                                                        ])
            for rule in field_rules :
                dom = expression.normalize_domain(safe_eval(rule.domain_force) if rule.domain_force else [])
                group_domains.setdefault(rule.group_ids[0], []).append(dom)
            if group_domains:
                group_domain = expression.OR(map(expression.OR, group_domains.values()))
                return group_domain
        return []
    
class FieldAccessMixin(models.AbstractModel):
    
    _name = 'domain.field.access.mixin'
    
    def _get_blacklist_field(self):
        "To be overridden in the inherited Model to define the black list field"
        return []
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
            Override fields_view_get to check field rule and update field domain
        """
        res = super(FieldAccessMixin, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        arch = etree.fromstring(res['arch'])
        for element in arch.iter() :
            # Check if field name belong to black field list
            if element.tag == 'field' and element.attrib.get('name') and element.attrib['name'] in self._get_blacklist_field() :
                # Get field domain
                domain_gp = self.pool.get('ir.field.rule').compute_domain(cr, uid, element.attrib['name'], self._name)
                if domain_gp :
                    domain = str(domain_gp)
                    # Check If any domain is already defined to the field
                    # Verify domain is not empty first
                    if element.attrib.get('domain') and element.attrib['domain'].replace(" ", "") != "[]":
                        # combine two domain with logical "&"
                        domain = "['&',%s,%s]" %(element.attrib['domain'][1:-1], domain[1:-1])
                    # Update domain attribute
                    element.attrib.update({'domain' : domain})
        res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$