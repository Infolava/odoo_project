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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class project_role_wizard(osv.osv_memory):
    
    _name = 'project.role.wizard'
    _description = "wizard to assign role to a project"
    _columns = {
                'role_ids' : fields.many2many('project.project.roles', string = 'Project Roles'),
                'project_role_ids' : fields.many2many('project.role', string = 'Assigned Roles'),
                }
    def _get_previous_assigned_ids(self, cr, uid, context):
        if (context is not None and 'active_model' in context.keys() and context['active_model'] == 'project.project'):
            previous_assigned_roles = self.pool.get('project.project').browse(cr, uid, [context['active_id']], context)[0]['project_role_ids']
            return [role.id for role in previous_assigned_roles]
        else :
            return []
        
    def _get_assigned_role_wizard(self, cr, uid, context):
        if (context is not None and 'active_model' in context.keys() and context['active_model'] == 'project.project'):
            return self.pool.get('project.role')._get_project_role_ids(cr, uid, context['active_ids'])
        else :
            return []

    def default_get(self, cr, uid, fields_list, context = None):
        default = super(project_role_wizard, self).default_get(cr, uid, fields_list, context)
        if 'role_ids' in fields_list :
            default['role_ids'] = self._get_previous_assigned_ids(cr, uid, context)
        if 'project_role_ids' in fields_list :
            default['project_role_ids'] = self._get_assigned_role_wizard(cr, uid, context)
        return default
    
    def assign_role(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids, context)
        role_ids = [role.id for role in wiz[0].role_ids]
        self.pool.get('project.project').write(cr, uid, [context['active_id']], {'project_role_ids' : [[6, False, role_ids]]})
        model_data_ids = self.pool.get('ir.model.data').search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'view_project_roles_wizard_effort_form')])
        resource_id = self.pool.get('ir.model.data').read(cr, uid, model_data_ids, fields = ['res_id'])[0]['res_id']
        return {'view_type':'form',
                'view_mode':'form',
                'name': 'Specify Needed Effort',
                'res_model':'project.role.wizard',
                'views':[(resource_id, 'form')],
                'type':'ir.actions.act_window',
                'target':'new',
                'context':context,
                }
        
    def assign_role_exit(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids, context)
        role_ids = [role.id for role in wiz[0].role_ids]
        self.pool.get('project.project').write(cr, uid, [context['active_id']], {'project_role_ids' : [[6, False, role_ids]]})
        return {
                'type': 'ir.actions.act_window_close',
                }
        
    def save_needed_effort(self, cr, uid, ids, context=None):
        return {
                'type': 'ir.actions.act_window_close',
                }
        
project_role_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$