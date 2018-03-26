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
# Created:               12 Dec 2014 14:40:34 by atrabelsi
# Last modified:      2014-12-12 14:40
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm

class project_role_wizard(models.TransientModel):
    
    _name = 'project.role.wizard'
    _description = "wizard to assign role to a project"

    role_ids = fields.Many2many('project.project.roles', string = 'Project Roles')
    project_role_ids = fields.Many2many('project.role', string = 'Assigned Roles')
    
    @api.model
    def _get_previous_assigned_ids(self):
        if self._context.get('active_model') == 'project.project':
            previous_assigned_roles = self.env['project.project'].browse([self._context['active_id']])[0]['project_role_ids']
            return [role.id for role in previous_assigned_roles]
        return []
        
    @api.model
    def _get_assigned_role_wizard(self):
        if (self._context.get('active_model') == 'project.project'):
            return self.env['project.role']._get_project_role_ids(self._context['active_ids'])
        return []

    @api.model
    def default_get(self, fields_list):
        default = super(project_role_wizard, self).default_get(fields_list)
        if 'role_ids' in fields_list :
            default['role_ids'] = self._get_previous_assigned_ids()
        if 'project_role_ids' in fields_list :
            default['project_role_ids'] = self._get_assigned_role_wizard()
        return default
    
    @api.multi
    def assign_role(self):
        self.ensure_one()
        role_ids = [role.id for role in self.role_ids]
        self.env['project.project'].browse(self._context['active_id']).write({'project_role_ids' : [[6, False, role_ids]]})
        resource_id = self.env.ref('project_role.view_project_roles_wizard_effort_form').id
        return {'view_type':'form',
                'view_mode':'form',
                'name': 'Specify Needed Effort',
                'res_model':'project.role.wizard',
                'views':[(resource_id, 'form')],
                'type':'ir.actions.act_window',
                'target':'new',
                'context':self._context,
                }
        
    @api.multi
    def assign_role_exit(self):
        self.ensure_one()
        role_ids = [role.id for role in self.role_ids]
        self.env['project.project'].browse(self._context['active_id']).write({'project_role_ids' : [[6, False, role_ids]]})
        return {
                'type': 'ir.actions.act_window_close',
                }
        
    @api.multi
    def save_needed_effort(self):
        return {
                'type': 'ir.actions.act_window_close',
                }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$