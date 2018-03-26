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
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

class project_role(models.Model):
    """
        Class to assign role (software_project_role) to a projects
        Association class between software_project_role and project_project (many2many relation)
    """

    _name = 'project.role'
    _rec_name = 'role_name'
    _description = 'Assign role to a project'

    @api.depends()
    def _get_selected_effort(self):
        for role in self :
            project_members = self.env['project.member'].search([('project_role_id', '=', role.id)])
            role.selected_effort = sum([member.hours_planned_monthly for member in project_members])

    project_id = fields.Many2one('project.project', string = 'Project', readonly = True)
    role_id = fields.Many2one('project.project.roles', string = 'Role', readonly = True)
    role_name = fields.Char(related='role_id.role_name', relation = 'project.project.roles', string = 'Role')
    hours_planned_monthly = fields.Integer(string = "Total Needed(Hours/Month)")
    selected_effort = fields.Integer(compute = _get_selected_effort, string = "Total Allocated(Hours/Month)")

    @api.depends('selected_effort')
    @api.constrains('hours_planned_monthly')
    def _check_selected_effort(self):
        for role in self :
            if role.hours_planned_monthly< 0 :
                raise ValidationError(_("Total Needed must be positive"))
#             if role.selected_effort > role.hours_planned_monthly:
#                 raise ValidationError(_("Selected effort exceed role's monthly average"))
    
    _sql_constraints = [
                        ('unique_project_role', 'UNIQUE (project_id, role_id)', _('Role already assigned to this project!')),
                        ]
    
    @api.model
    def _get_project_role_ids(self, project_ids, role_ids = []):
        """
            Return the list of project_role_ids
            @param project_ids = list of project ids
            @param role_ids = list of assigned role ids to the projects
        """
        domain = [('project_id', 'in', project_ids)]
        if role_ids :
            domain.append(('role_id', 'in', role_ids))
        return self.search(domain).ids

    @api.model
    def get_assigned_employees_project_roles(self, project_ids, assigned_role_ids):
        """
            Return the list of employee ids assigned to the specified roles in projects
            Return False if no assigned employees
            @param project_ids = list of project ids
            @param assigned_role_ids = list of assigned role ids to the projects
        """
        role_ids = self._get_project_role_ids(project_ids, assigned_role_ids)
        if role_ids :
            return self.env['project.member'].get_assigned_employees(role_ids)
        return []

    @api.multi
    def get_project_role_groups(self):
        """
            return the list of the groups related to a project role
            @param prj_role_ids : the project role id as list
        """
        self.ensure_one()
        return [gp.id for gp in self.role_id.related_group_ids]
    
    @api.multi
    def write(self, values):
        if values.has_key('project_id') or values.has_key('role_id') :
            raise except_orm(_('Operation Denied'), _('You can not modify a project role'))
        return super(project_role, self).write(values)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
