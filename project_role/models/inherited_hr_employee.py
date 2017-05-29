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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    
    _columns = {
                'user_id' : fields.many2one('res.users', required = True),
                }

    def _check_user_employee(self, cr, uid, ids):
        for employee in self.browse(cr, uid, ids) :
            if employee.user_id.id is False :
                return False
            elif len(employee.user_id.employee_ids) >1 :
                return False
        return True
    
    _constraints = [
                    (_check_user_employee, _("Selected user already assigned to an other employee "), ['user_id']),
                    ]
    
    def name_get(self, cr, uid, ids, context = None) :
        if context and context.has_key('current_model') and context['current_model'] == 'project.project' :
            result = []
            employee_names = super(hr_employee, self).name_get(cr, uid, ids, context)
            for employee_id, employee_name in employee_names :
                result.append((employee_id, employee_name + ', ' + str(self.browse(cr, uid, employee_id).availability)))
            return result
        return super(hr_employee, self).name_get(cr, uid, ids, context)
    
    def _get_working_hours_month_average(self, cr, uid, employee_id, context = None):
        from datetime import datetime, timedelta
        employee = self.browse(cr, uid, employee_id, context)
        employee_contract_id = employee.contract_id    # get only the last contract_id
        if employee_contract_id and employee_contract_id.working_hours :    # If the user has a contract
            start_date = datetime.strptime(employee_contract_id.date_start, "%Y-%m-%d")
            date_to = start_date + timedelta(days = 365)
            working_hours_month_average = int(round(self.pool.get('resource.calendar').interval_hours_get(cr, uid, employee_contract_id.working_hours.id, start_date, date_to) / 12))
        else :    # default working hours month average (8 hours/day, 20 working_days/month)
            working_hours_month_average = 160
        return working_hours_month_average

    def _get_availability(self, cr, uid, ids, field_name, arg, context = None):
        result = {}
        for employee_id in ids :
            # search only on open projects
            project_member_ids = self.pool.get('project.member').search(cr, uid, [('employee_id', '=', employee_id), ('project_id.state', 'in', ['open'])], context = context)
            project_members = self.pool.get('project.member').browse(cr, uid, project_member_ids, context)
            employee_effort = [member.effort_quotation for member in project_members]
            availability = self._get_working_hours_month_average(cr, uid, employee_id, context)
            result[employee_id] = availability - sum(employee_effort)
        return result

    _columns = {
                'availability' : fields.function(_get_availability, type = 'integer', string = 'Availability (Hours/Month)', readonly = True),
                'assigned_role_ids' : fields.one2many('project.member', 'employee_id', string = 'Assigned Roles'),
                }

    def create(self, cr, uid, values, context = None):
        emply_id =  super(hr_employee, self).create(cr, uid, values, context)
        if not self._check_user_employee(cr, uid, [emply_id]) :
            raise osv.except_osv(_('Operation denied !'), _('Selected user already assigned to an other employee'))
        return emply_id
    
hr_employee()

class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    
    def _check_user_employees(self, cr, uid, ids):
        for user in self.browse(cr, uid, ids) :
            if len(user.employee_ids) > 1 :
                return False
        return True
    
    _constraints = [
                    (_check_user_employees, _("A user must be related to at most one employee"), ['employee_ids']),
                    ]

res_users()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
