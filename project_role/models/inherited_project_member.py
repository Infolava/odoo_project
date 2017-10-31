# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2017 Infolava GmbH. All rights reserved.
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
# Created:               Jul 20, 2017 12:33:09 PM by atrabelsi
# Last modified:      2017-07-20 12:33
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
from calendar import monthrange

class project_member(models.Model):
    _name = "project.member"
    _inherit = 'project.member'
    
    @api.depends('employee_id')
    def _compute_total_and_real_planned(self):
        for project_member in self :
            role_start_dt = datetime.strptime(project_member.date_in_role_from, DF)
            role_end_dt = datetime.strptime(project_member.date_in_role_until, DF)
            real_planned = 0
            total_planned = 0
            date_from = role_start_dt
            while date_from < role_end_dt :
                date_to = date_from
                if date_from.month == role_end_dt.month and date_from.year == role_end_dt.year :
                    date_to = role_end_dt
                else :
                    date_to = date_to.replace(day = monthrange(date_from.year, date_from.month)[1])
                date_to = date_to + timedelta(days=1)
                project_role_availibility_hours = int(round(project_member.employee_id._get_total_working_hours(date_from, date_to)))
                planned_holidays = project_member.employee_id._compute_leaves(date_from, date_to)
                planned = min((project_role_availibility_hours - planned_holidays), project_member.hours_planned_monthly)
                real_planned += planned
                total_planned += planned + planned_holidays
                date_from = date_to
            project_member.hours_planned_real = real_planned
            project_member.hours_planned_total = total_planned
    
    @api.depends('hours_planned_real')
    def _compute_remaining_hours(self):
        for project_member in self :
            working_tasks = self.sudo().env["project.task.work"].search([('task_id.project_id','=', project_member.project_id.id),\
                                                                     ('user_id', '=', project_member.employee_id.user_id.id),\
                                                                     ('date', '>=',project_member.date_in_role_from),\
                                                                     ('date', '<=',project_member.date_in_role_until)
                                                                     ])

            spent_hours = sum([working_task.hours for working_task in working_tasks])
            project_member.hours_planned_remaining = project_member.hours_planned_real - spent_hours
    
    date_in_role_from = fields.Date(string = 'Date From', required = True)
    date_in_role_until = fields.Date(string = 'Date To', required = True)
    hours_planned_total = fields.Integer(compute = _compute_total_and_real_planned, string = 'Planned', readonly = True)
    hours_planned_real = fields.Integer(compute = _compute_total_and_real_planned, string = 'Real Planned', readonly = True)#effective hours
    hours_planned_remaining= fields.Integer(compute = _compute_remaining_hours, string = 'Remaining Hours', readonly = True)
    
    @api.one
    @api.constrains('date_in_role_from', 'date_in_role_until')
    def _check_dateFrom_vs_dateTo(self):
        for member in self :
            if member.date_in_role_from > member.date_in_role_until:
                raise ValidationError(_("The Date From should be later than the Date To"))
        return True
    
    @api.one
    @api.constrains('project_id', 'date_in_role_from', 'date_in_role_until')
    def _check_date_in_role_vs_project(self):
        for member in self :
            date_from = datetime.strptime(member.date_in_role_from, DF)
            date_until = datetime.strptime(member.date_in_role_until, DF)
            if member.project_id.date_start:
                prj_date_start = datetime.strptime(member.project_id.date_start, DF)
                if date_from < prj_date_start or date_until < prj_date_start:
                    raise ValidationError(_("The Date From should be later than the project start date"))
            if member.project_id.date:
                prj_date = datetime.strptime(member.project_id.date , DF)
                if date_from > prj_date or date_until > prj_date:
                    raise ValidationError(_("The End Date should be anterior than the project end date"))
        return True
    
    @api.one
    @api.constrains('employee_id', 'date_in_role_from', 'date_in_role_until')
    def _check_date_in_role_vs_contract(self):
        for member in self :
            if member.employee_id.contract_ids :
                start_date = min([datetime.strptime(contract.date_start, DF) for contract in member.employee_id.contract_ids])
                end_date = [datetime.strptime(contract.date_end, DF) for contract in member.employee_id.contract_ids if contract.date_end]
                if datetime.strptime(member.date_in_role_from, DF) < start_date :
                    raise ValidationError(_("The Date From and the Date Until should be included between contracts start date and end date"))
                if end_date and datetime.strptime(member.date_in_role_until , DF) > max(end_date) :
                    raise ValidationError(_("The Date From and the Date Until should be included between contracts start date and end date"))
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
