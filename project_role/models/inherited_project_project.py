# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2014 Infolava GmbH. All rights reserved.
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
# Created:               26 Nov 2014 15:50:52 by atrabelsi
# Last modified:      2014-11-26 15:50
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm

class project_project(models.Model):
    """
        Extend the Project Model : Assign a role to a project
    """
    _name = 'project.project'
    _inherit = 'project.project'

    #===========================================================================
    # @api.depends('employee_role_id')
    # def _get_project_members(self):
    #     for project in self :
    #         project_employees = [project_member.employee_id \
    #                              for project_member in project.employee_role_id \
    #                              if project_member.date_in_role_from <= fields.Date.today() \
    #                              and project_member.date_in_role_until >= fields.Date.today()]
    #         project.members =[[6, False, [employee_id.user_id.id for employee_id in project_employees]]]
    #===========================================================================
            
    project_role_ids = fields.Many2many('project.project.roles', 'project_role', 'project_id', 'role_id', string ='Software Project Role')
    assigned_role_id = fields.One2many('project.role', 'project_id', string ='Assigned Role', ondelete="cascade")
    employee_role_id = fields.One2many('project.member', 'project_id', string ='Project Members', ondelete="cascade")
    privacy_visibility = fields.Selection(default = 'members')
    #members = fields.Many2many(compute = _get_project_members, store = True)
    
    #===========================================================================
    # @api.model
    # def update_project_members(self):
    #     self.search([])._get_project_members()
    #===========================================================================
        
    @api.model
    def _get_visibility_selection(self):
        """ Override the _get_visibility_selection and add members visibility option. """
        selection = super(project_project, self)._get_visibility_selection()
        idx = [item[0] for item in selection].index('public')
        selection.insert((idx + 1), ('members', 'Project Members'))
        return selection
    
    @api.constrains('employee_role_id')
    def _check_employee_effort_availability(self):
        for project in self :
            for employee_role in project.employee_role_id :
                if employee_role.employee_id.availability < 0 :
                    raise ValidationError(_("Employee effort exceed his availability"))

    @api.constrains('assigned_role_id')
    def _check_selected_effort(self, cr, uid, ids):
        for project in self :
            for role in project.assigned_role_id :
                if role.selected_effort > role.hours_planned_monthly :
                    raise ValidationError(_("Selected effort exceed role's effort quotation"))

#     @api.constrains('members')
#     def _check_members_role(self, cr, uid, ids):
#         for project in self.browse(cr, uid, ids) :
#             for member in project.members :
#                 employee_ids = [employee.id for employee in member.employee_ids]
#                 if self.env['project.member'].search([('employee_id', 'in', employee_ids), ('project_id', '=', project.id)]) == [] :
#                     raise ValidationError(_("A user can not be a project member unless he is assigned to one role"))

    @api.multi
    def _get_previous_roles(self):
        """
            Return a list of assigned role ids for the project_id
        """
        self.ensure_one()
        return [projet_role.id for projet_role in self.project_role_ids]
    
    @api.multi
    def _update_project_users(self):
        self.ensure_one()
        project_employees = [project_member.employee_id.id for project_member in self.employee_role_id]
        if project_employees == [] :
            return self.write({'members':[[6, False, []]]})
        else :
            user_ids =[self.env['hr.employee'].browse([employee_id])[0].user_id.id for employee_id in project_employees]
            return self.write({'members':[[6, False, list(set(user_ids))]]})
        
    @api.model
    def create(self, values):
        if values.get('date') and values.get('date_start') :
            if fields.Date.from_string(values['date_start']) > fields.Date.from_string(values['date']):
                raise ValidationError(_("project start-date must be lower than project end-date"))
        return super(project_project, self).create(values)
             
    @api.multi
    def write(self, values):
        if values.get('date_start') :
            raise ValidationError( _("You can not edit the start date of the current project"))
        if values.get('date') :
            new_end_date = fields.Date.from_string(values['date'])
            employee_role = self.employee_role_id.filtered(lambda x : fields.Date.from_string(x.date_in_role_until) > new_end_date)
            if employee_role:
                employee_role.write({'date_in_role_until': values['date']})
        if values.has_key('project_role_ids') :
            for project in self :
                all_previous_roles_ids = project._get_previous_roles()
                #difference between the assigned roles and the the new list of roles
                role_to_withdraw = list(set(all_previous_roles_ids).difference(values['project_role_ids'][0][2]))
                if role_to_withdraw != [] and self.env['project.role'].get_assigned_employees_project_roles([project.id], role_to_withdraw) :
                    raise except_orm(_('Operation Denied'), \
                                         _('Some roles are assigned to users.\n Please withdraw the role from users before to withdraw the role from the project'))
                project_role_to_withdraw_ids = self.env['project.role'].search([('project_id', '=', project.id), ('role_id', 'in', role_to_withdraw)])
                project_role_to_withdraw_ids.unlink() #withdraw role from the project
                new_roles = list(set(values['project_role_ids'][0][2]).difference(all_previous_roles_ids)) # assign new roles to the project
                for new_role_id in new_roles :
                    self.env['project.role'].create({'project_id' :  project.id, 'role_id' : new_role_id})
            del values['project_role_ids']
        res = super(project_project, self).write(values)
        if values.has_key('employee_role_id') :
            for project in self :
                project._update_project_users()
        #self._check_members_role(cr, uid, ids)
        return res
    
    @api.multi
    def unlink(self):
        # ondelete cascade didn't work, force the elimination of project roles and project members 
        self.employee_role_id.unlink()
        return super(project_project, self).unlink()
    
    @api.model
    def assign_role_member_project(self):
        """
            Cron function to assign default role to existent project members.
        """
        # assign default role to all existent projects
        self.search([]).write({'project_role_ids' : [[6, False, [1]]]})
        for project in self.search([]) :
            project_members = project.members
            employee_ids = list(set([emply.id for emply in [member.employee_ids for member in project_members]]))
            for emp in employee_ids :
                project.write({'employee_role_id':[[0, False, 
                                                   {'project_role_id' : project.assigned_role_id[0].id, 
                                                    'employee_id' : emp, 
                                                    'hours_planned_monthly': 0} \
                                                   ]]\
                                                  })
        return

    @api.multi
    def get_closed_project_task_stage(self):
        self.ensure_one()
        return self.type_ids.filtered(lambda x : x.closed)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
