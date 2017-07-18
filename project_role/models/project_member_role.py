# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2015 Infolava GmbH. All rights reserved.
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
# Created:               15 May 2015 11:20:47 by atrabelsi
# Last modified:      2015-08-11 19:33:44
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import itertools
from datetime import date, datetime, timedelta, time
from calendar import monthrange

class project_role(osv.osv):
    """
        Class to assign role (software_project_role) to a projects
        Association class between software_project_role and project_project (many2many relation)
    """

    _name = 'project.role'
    _rec_name = 'role_name'
    _description = 'Assign role to a project'

    def _get_selected_effort(self, cr, uid, ids, field_name, arg, context = None):
        result = {}
        for role_id in ids :
            project_member_ids = self.pool.get('project.member').search(cr, uid, [('project_role_id', '=', role_id)], context = context)
            project_members = self.pool.get('project.member').browse(cr, uid, project_member_ids, context)
            selected_effort = [member.hours_planned_monthly for member in project_members]
            result[role_id] = sum(selected_effort)
        return result

    _columns = {
                'project_id' : fields.many2one('project.project', string = 'Project', readonly = True),
                'role_id' : fields.many2one('project.project.roles', string = 'Role', readonly = True),
                'role_name' : fields.related('role_id', 'role_name', relation = 'project.project.roles', type = 'char', string = 'Role'),
                'hours_planned_monthly' : fields.integer(string = "Total Needed(Hours/Month)"),
                'selected_effort' : fields.function(_get_selected_effort, type = 'integer', string = "Total Allocated(Hours/Month)"),
                }

    def _check_selected_effort(self, cr, uid, ids):
        for role in self.browse(cr, uid, ids) :
            if role.selected_effort > role.hours_planned_monthly:
                return False
        return True
    
    def _check_hours_planned_monthly(self, cr, uid, ids):
        for role in self.browse(cr, uid, ids) :
            if role.hours_planned_monthly< 0 :
                return False
        return True

    _constraints = [
                    (_check_selected_effort, _("Selected effort exceed role's monthly average"), ['hours_planned_monthly']),
                    (_check_hours_planned_monthly, _("Total Needed must be positive"), ['hours_planned_monthly']),
                    ]

    _sql_constraints = [
                        ('unique_project_role', 'UNIQUE (project_id, role_id)', _('Role already assigned to this project!')),
                        ]
    
    def _get_project_role_ids(self, cr, uid, project_ids, role_ids = [], context = None):
        """
            Return the list of project_role_ids
            @param project_ids = list of project ids
            @param role_ids = list of assigned role ids to the projects
        """
        if role_ids != [] :
            return self.search(cr, uid, [('project_id', 'in', project_ids), ('role_id', 'in', role_ids)], context = context)
        else :
            return self.search(cr, uid, [('project_id', 'in', project_ids)], context = context)

    def get_assigned_employees_project_roles(self, cr, uid, project_ids, assigned_role_ids, context = None):
        """
            Return the list of employee ids assigned to the specified roles in projects
            Return False if no assigned employees
            @param project_ids = list of project ids
            @param assigned_role_ids = list of assigned role ids to the projects
        """
        role_ids = self._get_project_role_ids(cr, uid, project_ids, assigned_role_ids, context)
        if role_ids != [] :
            return self.pool.get('project.member').get_assigned_employees(cr, uid, role_ids, context)
        return []

    def get_project_role_groups(self, cr, uid, prj_role_ids, context = None):
        """
            return the list of the groups related to a project role
            @param prj_role_ids : the project role id as list
        """
        prj_role = self.browse(cr, uid, prj_role_ids, context)[0]
        role_group_ids = [gp.id for gp in prj_role.role_id.related_group_ids]
        return role_group_ids
    
    def write(self, cr, uid, ids, values, context = None):
        if values.has_key('project_id') or values.has_key('role_id') :
            raise osv.except_osv(_('Operation Denied'), _('You can not modify a project role'))
        return super(project_role, self).write(cr, uid, ids, values, context)
    
project_role()

class project_member_role(osv.osv):
    """
        Class to assign a project role to an employee
    """
    _name = 'project.member'
    _description = 'Assign employee to a project'
    
    def _compute_total_planned(self, cr, uid, ids, field_name, arg, context = None):
        result = {}
        for project_member in self.browse(cr, uid, ids, context) :
            result [project_member.id] = project_member.hours_planned_real + \
            project_member.employee_id._compute_approved_leaves(project_member.date_in_role_from, project_member.date_in_role_until) +\
            project_member.employee_id._compute_public_holidays(project_member.date_in_role_from, project_member.date_in_role_until) 
        return result
     
    def _compute_real_planned(self, cr, uid, ids, field_name, arg, context = None):
        result = {}
        for project_member in self.browse(cr, uid, ids, context) :
            role_start_dt = project_member.employee_id._setup_date_timezone(project_member.date_in_role_from)
            role_end_dt = project_member.employee_id._setup_date_timezone(project_member.date_in_role_until)
            real_planned = 0
            date_from = role_start_dt
            while date_from < role_end_dt :
                date_to = date_from
                if date_from.month == role_end_dt.month and date_from.year == role_end_dt.year :
                    date_to = role_end_dt
                else :
                    date_to = date_to.replace(day = monthrange(date_from.year, date_from.month)[1])
                date_to = date_to + timedelta(days=1)
                project_role_availibility_hours = int(round(project_member.employee_id._get_total_working_hours(date_from,date_to)))
                real_planned += min(project_role_availibility_hours, project_member.hours_planned_monthly)
                date_from = date_to
            result[project_member.id] = real_planned
        return result
    
    def _compute_remaining_hours(self, cr, uid, ids, field_name, arg, context = None):
        result = {}
        for project_member in self.browse(cr, uid, ids, context) :
            work_ids = self.pool.get("project.task.work").search(cr, SUPERUSER_ID, \
                                                                    [('task_id.project_id','=', project_member.project_id.id),\
                                                                     ('user_id', '=', project_member.employee_id.user_id.id),\
                                                                     ('date', '>=',project_member.date_in_role_from),\
                                                                     ('date', '<=',project_member.date_in_role_until)
                                                                     ])
            working_task = self.pool.get("project.task.work").browse(cr, SUPERUSER_ID, work_ids)

            spent_hours = sum([working_task.hours for working_task in working_task])
            result [project_member.id] = project_member.hours_planned_real - spent_hours
        return result
    
    _columns = {
                'project_id' : fields.many2one('project.project', string = 'Project', readonly = True),
                'project_role_id' : fields.many2one('project.role', string = 'Role', required = True),
                'hours_planned_monthly' : fields.integer(string = "Monthly Average", required = True),
                'employee_id' : fields.many2one('hr.employee', string = 'Members', required = True),
                'date_in_role_from': fields.date(string = 'Date From', required = True),
                'date_in_role_until': fields.date(string = 'Date To', required = True),
                'hours_planned_total': fields.function(_compute_total_planned, type = 'integer', string = 'Planned', readonly = True),
                'hours_planned_real': fields.function(_compute_real_planned, type = 'integer', string = 'Real Planned', readonly = True),#effective hours
                'hours_planned_remaining': fields.function(_compute_remaining_hours, type = 'integer', string = 'Remaining Hours', readonly = True),
                }
    
    def _check_employee_effort(self, cr, uid, ids):
        for member in self.browse(cr, uid, ids) :
            if  member.hours_planned_monthly< 0 :
                return False
        return True

    def _check_role_in_project(self, cr, uid, ids):
        for member in self.browse(cr, uid, ids) :
            if member.project_role_id.project_id.id != member.project_id.id :
                return False
        return True
    
    def _check_date_in_role_from(self, cr, uid, ids):
        for member in self.browse(cr, uid, ids) :
            if member.project_id.date_start:
                if member.date_in_role_from  < member.project_id.date_start or member.date_in_role_until < member.project_id.date_start:
                    return False
            if member.project_id.date:
                if member.date_in_role_from  > member.project_id.date or member.date_in_role_until > member.project_id.date:
                    return False
        return True
    
    _constraints = [
                    (_check_employee_effort, _("Employee effort must be positive"), ['hours_planned_monthly']),
                    (_check_role_in_project, _("Role must belong to the project"), ['project_role_id', 'project_id']),
                    (_check_date_in_role_from, _("The Date From and the Date Until should be included between the project Start Date and End Date"), ['date_in_role_from', 'date_in_role_until']),
                    ]
    _sql_constraints = [
                        ('unique_employee_project_role', 'UNIQUE (project_role_id, employee_id)', _('Employee already assigned to this role!')),
                        ]


    def get_employee_role(self, cr, uid, project_id, employee_id, context = None):
        project_members_role_ids = self.search(cr, uid, [('project_id', '=', project_id), ('employee_id', '=', employee_id)], context = context)
        return [member_role.project_role_id.id for member_role in self.browse(cr, uid, project_members_role_ids, context)]

    def get_assigned_employees(self, cr, uid, project_role_ids, context = None):
        """
            Return the list of employee ids assigned to the specified project_rolei_ids
            @param project_role_ids = list of assigned role ids to the projects
        """
        project_member_ids = self.search(cr, uid, [('project_role_id', 'in', project_role_ids)], context = context)
        if project_member_ids != [] :
            return [project_member.employee_id.id for project_member in self.browse(cr, uid, project_member_ids, context)]
        return []

    def update_employee_user_groups(self, cr, uid, employee_ids, context = None):
        """
            Update Users related to each employee with role groups
            @param employee_ids : the list of the employee ids to update 
        """
        employees = self.pool.get('hr.employee').browse(cr, uid, employee_ids, context)
        for employee in employees :
            employee_roles = [role.project_role_id.role_id for role in employee.assigned_role_ids]
            groups = [role.related_group_ids for role in employee_roles]
            group_role_ids = [group.id for group in itertools.chain.from_iterable(groups)]
            employee_user = self.pool.get('res.users').browse(cr, 1, [employee.user_id.id], context)
            user_assigned_gps = [group.id for group in employee_user[0].groups_id]
            updates = list(set(group_role_ids).difference(user_assigned_gps))
            if updates != [] : # update user groups with the new  groups
                groups_updates = zip([4] * len(updates), updates)
                self.pool.get('res.users').write(cr, SUPERUSER_ID, [employee.user_id.id], {'groups_id' : groups_updates}, context)
        return True

    def withdraw_employee_groups_users(self, cr, uid, project_members, context = None):
        """
            Delete role groups from the user related to the employee after withdrawing roles
            @param project_members : list of dictionaries of project_members records (read from project.members)
        """
        
        def get_diff_implied_grps(list_implied_grps):
            output = []
            for list_gps in list_implied_grps:
                output = list(set(output).difference(list_gps))+list(set(list_gps).difference(output))
            return output
        
        for prj_member in project_members:
            # get the list of groups assigned to user through project roles
            employee = self.pool.get('hr.employee').browse(cr, uid, [prj_member['employee_id'][0]], context)[0]
            employee_assigned_role = employee.assigned_role_ids
            epl_gps = [gp.project_role_id.role_id.related_group_ids for gp in employee_assigned_role]
            gps_id = [gp.id for gp in itertools.chain.from_iterable(epl_gps)]
            # get the list of groups assigned to user
            user_gps_id = employee.user_id.groups_id.ids
            # get the difference : extra user groups
            grp_diff = list(set(user_gps_id).difference(gps_id))
            role_group_ids = self.pool.get('project.role').get_project_role_groups(cr, uid, [prj_member['project_role_id'][0]], context)
            # get the common groups between extra user groups and the withdrawn roles
            updates = list(set(grp_diff).intersection(role_group_ids))
            if updates :
                #get implieds_ids groups from role groups
                implied_grps_ids = [gp.implied_ids.ids for gp in self.pool.get('res.groups').browse(cr, SUPERUSER_ID, role_group_ids, context)]
                implied_grps_ids = get_diff_implied_grps(implied_grps_ids)
                updates += implied_grps_ids
                groups_updates = zip([3] * len(updates), updates)
                self.pool.get('res.users').write(cr, SUPERUSER_ID, [employee.user_id.id], {'groups_id' : groups_updates}, context)
        return True
    
    def ensure_members_own_no_artifacts(self, cr, uid, project_members, context = None):
        """ 
            Raise Operation Denied Exception at first hit (member owns artifact)
            Returns True if none of the members is owner of a projects artifacts
        """ 
        for prj_mbr in project_members :
            role_group_ids = self.pool.get('project.role').get_project_role_groups(cr, uid, [prj_mbr['project_role_id'][0]], context)
            access_create_model_ids = self.pool.get('ir.model.access').search(cr, SUPERUSER_ID, [('group_id', 'in', role_group_ids), \
                                                                                                 ('active', '=', True), \
                                                                                                 ('perm_create', '=', True), \
                                                                                                 ('perm_write', '=', True), \
                                                                                                 #('model_id.model', 'not in', ['project.task']), \
                                                                                                 ('model_id.field_id.name', 'in', ['project_id']), \
                                                                                                 ('model_id.field_id.name', 'in', ['owner']), \
                                                                                                 ])
            model_names = list(set([model_access.model_id.model for model_access in self.pool.get('ir.model.access').browse(cr, SUPERUSER_ID, access_create_model_ids, context)]))
            for model in model_names:
                user_id = self.pool.get('hr.employee').browse(cr, SUPERUSER_ID, [prj_mbr['employee_id'][0]], context)[0].user_id
                owned_art = self.pool.get(model).search(cr, SUPERUSER_ID, [('owner', '=', user_id.id), ('project_id', '=', prj_mbr['project_id'][0])])
                if owned_art :
                    raise osv.except_osv(_('Operation Denied!\n'), _("Could not withdraw user %s from role %s. User owns some artifacts") % (user_id.name, prj_mbr['project_role_id'][1]))
        return True
            
    def create(self, cr, uid, values, context = None):
        res =  super(project_member_role, self).create(cr, uid, values, context)
        self.update_employee_user_groups(cr, uid, [values['employee_id']], context)
        return res

    def write(self, cr, uid, ids, values, context = None):
        project_members = self.browse(cr, uid, ids, context)
        project_members_read = self.read(cr, uid, ids, context)
        if values.has_key('employee_id') or values.has_key('project_role_id') :
            self.ensure_members_own_no_artifacts(cr, uid, project_members_read, context)
        employee_ids = [member.employee_id.id for member in project_members]
        res = super(project_member_role, self).write(cr, uid, ids, values, context)
        if values.has_key('employee_id') or values.has_key('project_role_id') :
            self.withdraw_employee_groups_users(cr, uid, project_members_read, context)
            self.update_employee_user_groups(cr, uid, list(set(employee_ids)), context)
        return res
    
    def unlink(self, cr, uid, ids, context = None):
        project_members = self.read(cr, uid, ids, context = context)
        self.ensure_members_own_no_artifacts(cr, uid, project_members, context)
        res = super(project_member_role, self).unlink(cr, uid, ids, context)
        self.withdraw_employee_groups_users(cr, uid, project_members, context)
        return res

project_member_role()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
