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
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _ 
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta
import pytz
import math

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
    def _check_contract_working_hours(self):
        # check if the user has a contract with specified working hours
        self.ensure_one()
        for contract in self.contract_ids :
            if contract.working_hours :
                return True
        return False
    
    @api.multi
    def _get_working_hours_month_average(self):
        self.ensure_one()
        working_hours_month_average = 0
        if self._check_contract_working_hours() :
            for contract in self.contract_ids :
                date_from = datetime.strptime(contract.date_start, DF)
                date_to = date_from + timedelta(days = 365)
                if contract.date_end and date_to > datetime.strptime(contract.date_end, DF) :
                    date_to = datetime.strptime(contract.date_end, DF)
                num_month = math.ceil((date_to - date_from).days / 30.0)
                working_hours_month_average += int(round(contract.working_hours.get_working_hours(\
                                                          date_from, date_to, compute_leaves = False)[0] / num_month))
        else :    # default working hours month average (8 hours/day, 21 working_days/month)
            working_hours_month_average = 168
        return working_hours_month_average

    @api.multi
    def _get_total_working_hours(self, dt_from, dt_until = False):
        """
            get total working hours from dt_from to dt_until considering all employee contracts.
            If dt_until is not specified , compute total working hours of date dt_from
            @param dt_from: datetime, starting date
            @param dt_from: datetime, ending date
            @return: float, Total working hours
        """
        self.ensure_one()
        hours = 0.0
        if dt_until :
            for contract in self.contract_ids :
                #Do not compute leaves
                # Change context time zone to UTC, not consider user timezone when computing working hours
                hours += contract.with_context(tz=pytz.utc._tzname).working_hours.get_working_hours(dt_from, dt_until, compute_leaves = False)[0]
        else :
            for contract in self.contract_ids :
                hours += contract.working_hours.get_working_hours_of_date(dt_from)[0]
        return hours
    
    def _compute_monthly_availability_average(self):
        for employee in self :
            # search only on open projects
            project_members = self.sudo().env['project.member'].search([('employee_id', '=', employee.id), \
                                                                 ('project_id.state', 'in', ['open'])])
            total_hours_planned_monthly = [member.hours_planned_monthly for member in project_members]
            employee.availability = employee._get_working_hours_month_average() - sum(total_hours_planned_monthly)
    
    def _datetime_to_tz(self, date, tz=pytz.utc._tzname):
        """
            Convert datetime to specified time zone
        """
        
        tz_info = pytz.timezone(tz) # equivalent to fields.datetime.context_timestamp(cr, uid, dt_from, context=context).tzinfo
        return datetime.strptime(date, DTF).replace(tzinfo=pytz.UTC).astimezone(tz_info).replace(tzinfo=None)
        
    @api.multi
    def _compute_leaves(self, dt_from, dt_until):
        self.ensure_one()
        return self._compute_approved_leaves(dt_from, dt_until) + self._compute_public_holidays(dt_from, dt_until)
    
    @api.multi
    def _compute_approved_leaves(self, dt_from, dt_until):
        """
            Compute employee approved leaves for specific period
            @param dt_from: datetime, starting date
            @param dt_from: datetime, ending date
            @return: float, Total approved leaves hours
        """
        self.ensure_one()
        holidays = self.env['hr.holidays'].search([('state','=','validate'),\
                                                       ('employee_id','=',self.id), \
                                                       ('type','=','remove'), \
                                                       ('date_to', '>=', str(dt_from)), \
                                                       ]\
                                                      )
        hours = 0.0
        for hol in holidays :
            date_from = hol.date_from if datetime.strptime(hol.date_from, DTF) >= dt_from else str(dt_from)
            date_to = hol.date_to if datetime.strptime(hol.date_to, DTF) <= dt_until else str(dt_until)
            #Use holiday create_uid timezone instead of employee timezone
            date2tz_from = self._datetime_to_tz(date_from, hol.create_uid.tz or pytz.utc._tzname)
            date2tz_to = self._datetime_to_tz(date_to, hol.create_uid.tz or pytz.utc._tzname)
            hours += self._get_total_working_hours(date2tz_from, date2tz_to)
        return hours
    
    #===========================================================================
    # @api.multi
    # def _compute_public_holidays(self, dt_from, dt_until):
    #     """
    #         compute total working hours of public holidays
    #         @param dt_from: datetime, starting date
    #         @param dt_from: datetime, ending date
    #         @return: float
    #     """
    #     hours = 0.0
    #     while dt_from <= dt_until:
    #         if self.pool.get('hr.holidays.public').is_public_holiday(self._cr, SUPERUSER_ID, dt_from):
    #             hours += self._get_total_working_hours(dt_from)
    #         dt_from = dt_from + timedelta(days=1)
    #     return hours
    #===========================================================================

    user_id = fields.Many2one('res.users', required = True)
    contract_ids = fields.One2many('hr.contract', 'employee_id', 'Contracts', required = True)
    availability = fields.Integer(compute = _compute_monthly_availability_average, string = 'Monthly Availability Average (Hours/Month)', readonly = True)
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
