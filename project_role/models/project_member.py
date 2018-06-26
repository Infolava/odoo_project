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
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm
from datetime import timedelta
from calendar import monthrange
import itertools

class project_member(models.Model):
    _name = "project.member"
    
    @api.depends('employee_id')
    def _compute_total_and_real_planned(self):
        for project_member in self :
            # Convert to datetime type to be used by compute working hours
            role_start_dt = fields.Datetime.from_string(project_member.date_in_role_from)
            role_end_dt = fields.Datetime.from_string(project_member.date_in_role_until)
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
            
    @api.model
    def _get_date_end(self):
        if self._context.get('project_id') :
            return self.env['project.project'].browse(self._context.get('project_id')).date
        
    project_id = fields.Many2one('project.project', string = 'Project', readonly = True)
    project_role_id = fields.Many2one('project.role', string = 'Role', required = True)
    hours_planned_monthly = fields.Integer(string = "Monthly Average", required = True)
    employee_id = fields.Many2one('hr.employee', string = 'Members', required = True)
    date_in_role_from = fields.Date(string = 'Date From', required = True, default = fields.Date.today())
    date_in_role_until = fields.Date(string = 'Date To', required = True, default = _get_date_end)
    hours_planned_total = fields.Integer(compute = _compute_total_and_real_planned, string = 'Planned', readonly = True)
    hours_planned_real = fields.Integer(compute = _compute_total_and_real_planned, string = 'Real Planned', readonly = True)#effective hours
    hours_planned_remaining= fields.Integer(compute = _compute_remaining_hours, string = 'Remaining Hours', readonly = True)
    
    @api.depends('project_role_id')
    @api.constrains('hours_planned_monthly')
    def _check_employee_effort(self):
        for member in self :
            if member.hours_planned_monthly < 0 :
                raise ValidationError( _("Employee effort must be positive"))
            if member.project_role_id.selected_effort > member.project_role_id.hours_planned_monthly:
                raise ValidationError(_("Selected effort exceed role's monthly average"))

    @api.constrains('project_role_id', 'project_id')
    def _check_role_in_project(self):
        for member in self :
            if member.project_role_id.project_id.id != member.project_id.id :
                raise ValidationError( _("Role must belong to the project"))
    
    @api.constrains('date_in_role_from', 'date_in_role_until')
    def _check_dateFrom_vs_dateTo(self):
        for member in self :
            if member.date_in_role_from > member.date_in_role_until:
                raise ValidationError(_("The Date From should be later than the Date To"))
        return True
    
    @api.constrains('project_id', 'date_in_role_from', 'date_in_role_until')
    def _check_date_in_role_vs_project(self):
        for member in self :
            date_from = fields.Date.from_string(member.date_in_role_from)
            date_until = fields.Date.from_string(member.date_in_role_until)
            if member.project_id.date_start:
                prj_date_start = fields.Date.from_string(member.project_id.date_start)
                if date_from < prj_date_start or date_until < prj_date_start:
                    raise ValidationError(_("The Date From should be later than the project start date"))
            if member.project_id.date:
                prj_date = fields.Date.from_string(member.project_id.date)
                if date_from > prj_date or date_until > prj_date:
                    raise ValidationError(_("The End Date should be anterior than the project end date"))
        return True
    
    @api.constrains('employee_id', 'date_in_role_from', 'date_in_role_until')
    def _check_date_in_role_vs_contract(self):
        for member in self :
            if member.employee_id.contract_ids :
                start_date = min([fields.Date.from_string(contract.date_start) for contract in member.employee_id.contract_ids])
                end_date = [fields.Date.from_string(contract.date_end) for contract in member.employee_id.contract_ids if contract.date_end]
                if fields.Date.from_string(member.date_in_role_from) < start_date :
                    raise ValidationError(_("The Date From and the Date Until should be included between contracts start date and end date"))
                if end_date and fields.Date.from_string(member.date_in_role_until) > max(end_date) :
                    raise ValidationError(_("The Date From and the Date Until should be included between contracts start date and end date"))
        return True
    
    @api.constrains('employee_id', 'project_role_id', 'date_in_role_from', 'date_in_role_until')
    def _check_duplicated_role(self):
        for record in self :
            dt_from = fields.Date.from_string(record.date_in_role_from)
            dt_until = fields.Date.from_string(record.date_in_role_until)
            same_role = self.search([('employee_id', '=', record.employee_id.id), \
                                     ('project_role_id', '=', record.project_role_id.id), \
                                     '!', '|', '&',
                                     ('date_in_role_from', '>=', dt_until), \
                                     ('date_in_role_until', '>=', dt_until), \
                                     '&',
                                     ('date_in_role_from', '<=', dt_from), \
                                     ('date_in_role_until', '<=', dt_from), \
                                     ])# - record
            if same_role != record:
                raise ValidationError("%s already assigned to role %s in the same period %s -> %s." \
                                      %(record.employee_id.name_related, record.project_role_id.role_name, record.date_in_role_from, record.date_in_role_until)
                                      )
                
    @api.model
    def get_employee_role(self, project_id, employee_id) :
        project_members_roles = self.search([('project_id', '=', project_id), ('employee_id', '=', employee_id)])
        return [member_role.project_role_id.id for member_role in project_members_roles]
    
    @api.model
    def get_assigned_employees(self, project_role_ids):
        """
            Return the list of employee ids assigned to the specified project_rolei_ids
            @param project_role_ids = list of assigned role ids to the projects
        """
        project_member_ids = self.search([('project_role_id', 'in', project_role_ids)])
        return [project_member.employee_id.id for project_member in project_member_ids]
    
    @api.model
    def update_employee_user_groups(self, employee_ids):
        """
            Update Users related to each employee with role groups
            @param employee_ids : the list of the employee ids to update 
        """
        for employee in self.env['hr.employee'].browse(employee_ids) :
            employee_roles = []
            for empl_ass_role in employee.assigned_role_ids :
                if empl_ass_role.date_in_role_from <= fields.Date.today() and empl_ass_role.date_in_role_until >= fields.Date.today():
                    employee_roles += empl_ass_role.project_role_id.role_id
            #employee_roles = [role.project_role_id.role_id for role in employee.assigned_role_ids]
            
            groups = [role.related_group_ids for role in employee_roles]
            group_role_ids = [group.id for group in itertools.chain.from_iterable(groups)]
            user_assigned_gps = [group.id for group in employee.user_id[0].groups_id]
            updates = list(set(group_role_ids).difference(user_assigned_gps))
            if updates != [] : # update user groups with the new  groups
                groups_updates = zip([4] * len(updates), updates)
                employee.user_id.sudo().write({'groups_id' : groups_updates})
        return True
    
    @api.model
    def withdraw_employee_groups_users(self, project_members):
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
            employee = self.env['hr.employee'].browse([prj_member['employee_id'][0]])[0]
            employee_assigned_role = employee.assigned_role_ids
            epl_gps = []
            for empl_ass_role in employee_assigned_role :
                if empl_ass_role.date_in_role_until >= fields.Date.today():
                    epl_gps +=[empl_ass_role.project_role_id.role_id.related_group_ids] 
            #epl_gps = [gp.project_role_id.role_id.related_group_ids for gp in employee_assigned_role]
            gps_id = [gp.id for gp in itertools.chain.from_iterable(epl_gps)]
            # get the list of groups assigned to user
            user_gps_id = employee.user_id.groups_id.ids
            # get the difference : extra user groups
            grp_diff = list(set(user_gps_id).difference(gps_id))
            role_group_ids = self.env['project.role'].browse([prj_member['project_role_id'][0]]).get_project_role_groups()
            # get the common groups between extra user groups and the withdrawn roles
            updates = list(set(grp_diff).intersection(role_group_ids))
            if updates :
                #get implieds_ids groups from role groups
                implied_grps_ids = [gp.implied_ids.ids for gp in self.env['res.groups'].browse(role_group_ids)]
                implied_grps_ids = get_diff_implied_grps(implied_grps_ids)
                updates += implied_grps_ids
                groups_updates = zip([3] * len(updates), updates)
                employee.user_id.sudo().write({'groups_id' : groups_updates})
        return True
    
    #===========================================================================
    # @api.model
    # def delete_employee_groups_users(self, project_members):
    #     """
    #         Delete role groups from the user related to the employee after withdrawing roles
    #         @param project_members : list of dictionaries of project_members records (read from project.members)
    #     """
    #     def get_diff_implied_grps(list_implied_grps):
    #         output = []
    #         for list_gps in list_implied_grps:
    #             output = list(set(output).difference(list_gps))+list(set(list_gps).difference(output))
    #         return output
    #     
    #     for prj_member in project_members:
    #         # get the list of groups assigned to user through project roles
    #         employee = self.env['hr.employee'].browse([prj_member['employee_id'][0]])[0]
    #         employee_assigned_role = employee.assigned_role_ids
    #         epl_gps = []
    #         for empl_ass_role in employee_assigned_role :
    #             if empl_ass_role.date_in_role_until >= fields.Date.today():
    #                 epl_gps +=[empl_ass_role.project_role_id.role_id.related_group_ids] 
    #         #epl_gps = [gp.project_role_id.role_id.related_group_ids for gp in employee_assigned_role]
    #         gps_id = [gp.id for gp in itertools.chain.from_iterable(epl_gps)]
    #         # get the list of groups assigned to user
    #         user_gps_id = employee.user_id.groups_id.ids
    #         # get the difference : extra user groups
    #         grp_diff = list(set(user_gps_id).difference(gps_id))
    #         role_group_ids = self.env['project.role'].browse([prj_member['project_role_id'][0]]).get_project_role_groups()
    #         # get the common groups between extra user groups and the withdrawn roles
    #         updates = list(set(grp_diff).intersection(role_group_ids))
    #         if updates :
    #             #get implieds_ids groups from role groups
    #             implied_grps_ids = [gp.implied_ids.ids for gp in self.env['res.groups'].browse(role_group_ids)]
    #             implied_grps_ids = get_diff_implied_grps(implied_grps_ids)
    #             updates += implied_grps_ids
    #             groups_updates = zip([3] * len(updates), updates)
    #             employee.user_id.sudo().write({'groups_id' : groups_updates})
    #     return True
    #===========================================================================
    
    @api.model
    def ensure_members_own_no_artifacts(self, project_members):
        """ 
            Raise Operation Denied Exception at first hit (member owns artifact)
            Returns True if none of the members is owner of a projects artifacts
        """ 
        for prj_mbr in project_members :
            role_group_ids = self.env['project.role'].browse([prj_mbr['project_role_id'][0]]).get_project_role_groups()
            access_create_models = self.sudo().env['ir.model.access'].search([('group_id', 'in', role_group_ids), \
                                                                                 ('active', '=', True), \
                                                                                 ('perm_create', '=', True), \
                                                                                 ('perm_write', '=', True), \
                                                                                 #('model_id.model', 'not in', ['project.task']), \
                                                                                 ('model_id.field_id.name', 'in', ['project_id']), \
                                                                                 ('model_id.field_id.name', 'in', ['owner']), \
                                                                                 ])
            model_names = list(set([model_access.model_id.model for model_access in access_create_models]))
            for model in model_names:
                user_id = self.env['hr.employee'].browse([prj_mbr['employee_id'][0]])[0].user_id
                owned_art = self.env[model].search([('owner', '=', user_id.id), ('project_id', '=', prj_mbr['project_id'][0])])
                if owned_art :
                    raise except_orm(_('Operation Denied!\n'), _("Could not withdraw user %s from role %s. User owns some artifacts") % (user_id.name, prj_mbr['project_role_id'][1]))
        return True
    
    @api.model
    def create(self, values):
        res =  super(project_member, self).create(values)
        if res['date_in_role_from'] <= fields.Date.today() \
           and res['date_in_role_until'] >= fields.Date.today():
            self.update_employee_user_groups([values['employee_id']])
        return res

    @api.multi
    def write(self, values):
        project_members_read = self.read(['project_id', 'employee_id', 'project_role_id'])
        if values.has_key('employee_id') or values.has_key('project_role_id') :
            self.ensure_members_own_no_artifacts(project_members_read)
        res = super(project_member, self).write(values)
        if values.has_key('employee_id') or values.has_key('project_role_id') or values.has_key('date_in_role_from') or values.has_key('date_in_role_until'):
            employee_ids = [member.employee_id.id for member in self]
            self.withdraw_employee_groups_users(project_members_read)
            self.update_employee_user_groups(list(set(employee_ids)))
        return res
    
    @api.multi
    def unlink(self):
        project_members = self.read(['project_id', 'employee_id', 'project_role_id'])
        self.ensure_members_own_no_artifacts(project_members)
        res = super(project_member, self).unlink()
        self.withdraw_employee_groups_users(project_members)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
