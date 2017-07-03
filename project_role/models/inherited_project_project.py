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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class project(osv.osv):
    """
        Extend the Project Model : Assign a role to a project
    """
    _name = 'project.project'
    _inherit = 'project.project'
    
    _columns = {
                'project_role_ids' : fields.many2many('project.project.roles', 'project_role', 'project_id', 'role_id', string ='Software Project Role'),
                'assigned_role_id' : fields.one2many('project.role', 'project_id', string ='Assigned Role', ondelete="cascade"),
                'employee_role_id' : fields.one2many('project.member', 'project_id', string ='Project Members', ondelete="cascade"),
                }
    
    def _get_visibility_selection(self, cr, uid, context=None):
        """ Override the _get_visibility_selection and add members visibility option. """
        selection = super(project, self)._get_visibility_selection(cr, uid, context=context)
        idx = [item[0] for item in selection].index('public')
        selection.insert((idx + 1), ('members', 'Project Members'))
        return selection
    
    def _check_employee_effort_availability(self, cr, uid, ids):
        for project in self.browse(cr, uid, ids) :
            for employee_role in project.employee_role_id :
                if employee_role.employee_id.availability < 0 :
                    return False
        return True

    def _check_selected_effort(self, cr, uid, ids):
        for project in self.browse(cr, uid, ids) :
            for role in project.assigned_role_id :
                if role.selected_effort > role.hours_planned_monthly :
                    return False
        return True

    def _check_members_role(self, cr, uid, ids):
        for project in self.browse(cr, uid, ids) :
            for member in project.members :
                employee_ids = [employee.id for employee in member.employee_ids]
                if self.pool.get('project.member').search(cr, uid, [('employee_id', 'in', employee_ids), ('project_id', '=', project.id)]) == [] :
                    raise osv.except_osv(_('Operation Denied'), _("A user can not be a project member unless he is assigned to one role"))
        return True
    
    _constraints = [
                    (_check_employee_effort_availability, _("Employee effort exceed his availability"), ['employee_role_id']),
                    (_check_selected_effort, _("Selected effort exceed role's effort quotation"), ['employee_role_id']),
                    ]
    
    _defaults = {
                 'privacy_visibility': 'members',
                 }
    
#     def create(self, cr, uid, values, context = None):
#         prj_id = super(project, self).create(cr, uid, values, context)
#         self._check_members_role(cr, uid, [prj_id])
#         return prj_id 
    
    def _get_previous_roles(self, cr, uid, project_id, context):
        """
            Return a list of assigned role ids for the project_id
        """
        project = self.browse(cr, uid, project_id, context)
        return [projet_role.id for projet_role in project.project_role_ids]
     
    def _update_project_users(self, cr, uid, project_id, context = None):
        project = self.browse(cr, uid, [project_id], context)[0]
        project_employees = [project_member.employee_id.id for project_member in project.employee_role_id]
        if project_employees == [] :
            return self.write(cr, uid, [project_id], {'members':[[6, False, []]]})
        else :
            user_ids =[self.pool.get('hr.employee').browse(cr, uid, [employee_id], context)[0].user_id.id for employee_id in project_employees]
            return self.write(cr, uid, [project_id], {'members':[[6, False, list(set(user_ids))]]})
        
    def write(self, cr, uid, ids, values, context = None):
        if values.has_key('project_role_ids') :
            for project_id in ids :
                all_previous_roles_ids = self._get_previous_roles(cr, uid, project_id, context)
                #difference between the assigned roles and the the new list of roles
                role_to_withdraw = list(set(all_previous_roles_ids).difference(values['project_role_ids'][0][2]))
                if role_to_withdraw != [] and self.pool.get('project.role').get_assigned_employees_project_roles(cr, uid, [project_id], role_to_withdraw, context) != [] :
                    raise osv.except_osv(_('Operation Denied'), \
                                         _('Some roles are assigned to users.\n Please withdraw the role from users before to withdraw the role from the project'))
                project_role_to_withdraw_ids = self.pool.get('project.role').search(cr, uid, [('project_id', '=', project_id), ('role_id', 'in', role_to_withdraw)])
                self.pool.get('project.role').unlink(cr, uid, project_role_to_withdraw_ids, context) #withdraw role from the project
                new_roles = list(set(values['project_role_ids'][0][2]).difference(all_previous_roles_ids)) # assign new roles to the project
                for new_role_id in new_roles :
                    self.pool.get('project.role').create(cr, uid, {'project_id' :  project_id, 'role_id' : new_role_id}, context)
            del values['project_role_ids']
        res = super(project, self).write(cr, uid, ids, values, context)
        if values.has_key('employee_role_id') :
            for project_id in ids :
                self._update_project_users(cr, uid, project_id, context)
        #self._check_members_role(cr, uid, ids)
        return res
    
    def unlink(self, cr, uid, ids, context = None):
        # ondelete cascade didn't work, force the elimination of project roles and project members 
        project_members = self.pool.get('project.member').search(cr, uid, [('project_id', 'in', ids)], context = context)
        self.pool.get('project.member').unlink(cr, uid, project_members, context)
        project_roles = self.pool.get('project.role').search(cr, uid, [('project_id', 'in', ids)], context = context)
        self.pool.get('project.role').unlink(cr, uid, project_roles, context)
        return super(project, self).unlink(cr, uid, ids, context)
    
    def assign_role_member_project(self, cr, uid, ids = False, context = None):
        """
            Cron function to assign default role to existent project members.
        """
        if context == None :
            context = {}
        if not ids :
            ids = self.search(cr, uid, [], context = context)
        # assign default role to all existent projects
        self.write(cr, uid, ids, {'project_role_ids' : [[6, False, [1]]]}, context)
        for project_id in ids :
            project = self.browse(cr, uid, [project_id], context)[0]
            project_members = project.members
            employee_ids = list(set([emply.id for emply in [member.employee_ids for member in project_members]]))
            for emp in employee_ids :
                self.write(cr, uid, [project_id], {'employee_role_id':[[0, False, 
                                                                       {'project_role_id' : project.assigned_role_id[0].id, 
                                                                        'employee_id' : emp, 
                                                                        'hours_planned_monthly': 0} \
                                                                       ]]\
                                                  }, context)
        return
project()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
