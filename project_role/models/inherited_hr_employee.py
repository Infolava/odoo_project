# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2016 Infolava GmbH. All rights reserved.
# License:
# --------------------------------------------------------------------------------
#    This file is part of TransALM
#
#    TransALM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Created:               Mar 14, 2016 11:31:27 AM by atrabelsi
# Last modified:      2016-03-14 11:31
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta

class hr_employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"
    
    @api.one
    @api.constrains('user_id')
    def _check_user_employee_relation(self):
        if not self.user_id :
            raise ValidationError(_("Please select related user."))
        elif len(self.user_id.employee_ids) >1:
            raise ValidationError(_("Selected user already assigned to an other employee."))
    
#     @api.one
#     @api.constrains('contract_ids') 
#     def _check_employee_contract(self):
#         if not self.contract_ids :
#             raise ValidationError(_("Please select employee contract."))

    @api.multi
    def name_get(self) :
        if self._context and self._context.has_key('current_model') and self._context['current_model'] == 'project.project' :
            result = []
            for employee in self:
                result.append((employee.id, employee.name + ', ' + str(employee.availability)))
            return result
        return super(hr_employee, self).name_get()
    
    @api.multi
    def _get_working_hours_month_average(self):
        self.ensure_one()
        employee_contract_id = self.contract_id    # get only the last contract_id
        if employee_contract_id and employee_contract_id.working_hours :    # If the user has a contract
            start_date = datetime.strptime(employee_contract_id.date_start, DF)
            date_to = start_date + timedelta(days = 365)
            working_hours_month_average = int(round(employee_contract_id.working_hours.interval_hours_get(start_date, date_to)[0] / 12))
        else :    # default working hours month average (8 hours/day, 20 working_days/month)
            working_hours_month_average = 160
        return working_hours_month_average


    def _get_availability(self):
        for employee in self :
            # search only on open projects
            project_members = self.env['project.member'].search([('employee_id', '=', employee.id), \
                                                                 ('project_id.state', 'in', ['open'])])
            employee_effort = [member.hours_planned_monthly for member in project_members]
            employee.availability = employee._get_working_hours_month_average() - sum(employee_effort)
            
    @api.multi
    def _compute_approved_leaves(self, dt_from, dt_until):
        """
            Compute employee approved leaves for specific period
            @ param : d
        """
        self.ensure_one()
        holidays = self.env['hr.holidays'].search([('state','=','validate'),\
                                                       ('employee_id','=',self.id), \
                                                       ('type','=','remove'), \
                                                       ('date_from', '>=', dt_from), \
                                                       ('date_to', '<=', dt_until)\
                                                       ]\
                                                      )
        hours = 0.0
        for hol in holidays :
            date_from = datetime.strptime(hol.date_from, DTF)
            date_to = datetime.strptime(hol.date_to, DTF)
            if self.contract_id and self.contract_id.working_hours:
                hours += self.contract_id.working_hours.get_working_hours(date_from, date_to)[0]
        return hours

    user_id = fields.Many2one('res.users', required = True)
    contract_ids = fields.One2many('hr.contract', 'employee_id', 'Contracts', required = True)
    availability = fields.Integer(compute = _get_availability, string = 'Availability (Hours/Month)', readonly = True)
    assigned_role_ids = fields.One2many('project.member', 'employee_id', string = 'Assigned Roles')
    
class res_users(models.Model):
    _name = "res.users"
    _inherit = "res.users"
    
    @api.one
    @api.constrains('employee_ids')
    def _check_user_employees(self):
        if len(self.employee_ids) > 1 :
            raise ValidationError(_("A user must be related to at most one employee"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
