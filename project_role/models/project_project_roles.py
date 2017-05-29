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
# --------------------------------------------------------------------------------
# Created:               25 Nov 2014 09:02:22 by atrabelsi
# Last modified:      2017-05-05 03:45:20 PM
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class project_project_role(osv.osv):
    
    _name = 'project.project.roles'
    _description = 'Define and specify software project roles'
    _rec_name = 'role_name'
    _columns = {
                'role_name' :  fields.char(string = 'Name', required = True, translate = True),
                'description' : fields.char(string = 'Description', translate = True),
                'related_group_ids' : fields.many2many('res.groups', rel = 'project_roles_groups_rel', string = 'Groups', required = True,),
                }

    _sql_constraints = [
                        ('unique_role_name', 'UNIQUE (role_name)', _('Role already exists!')),
                        ]
    
    def create(self, cr, uid, values, context = None):
        if values.has_key('related_group_ids') and (values['related_group_ids'] == [[6, False, []]] or not values['related_group_ids']):
            raise osv.except_osv(_('Validate Error'), _('Please Choose a related group to the role'))
        role_ids = self.search(cr, SUPERUSER_ID, [('related_group_ids', 'in', values['related_group_ids'][0][2])], context=context)
        if (isinstance(role_ids, list) and len(role_ids)> 0):
            for role in self.browse(cr, uid, role_ids) :
                if role.related_group_ids.ids == values['related_group_ids'][0][2] :
                    raise osv.except_osv(_('Validate Error'), _('A role with the same groups exists already!'))
        return super(project_project_role, self).create(cr, uid, values, context)
    
    def get_name_projects_associated(self, cr, uid, role_ids, context=None):
        """
        Finds projects associated with role
        :param role_ids
        :return list of string with names of the associated projects
        """
        project_ids = self.pool.get('project.project').search(cr, SUPERUSER_ID, [('project_role_ids.id', 'in', role_ids)], context=context)
        if project_ids and len(project_ids) > 0:
            return [prj.name for prj in self.pool.get('project.project').browse(cr, SUPERUSER_ID, project_ids, context=context)]
        return []
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Override orm.unlink() to prohibit deleting roles that are associated to some projects
        """
        project_names = self.get_name_projects_associated(cr, uid, ids, context)
        if len(project_names) > 0:
            raise osv.except_osv(_('Operation not permitted !'), _('You can not delete roles associated to projects!\nThis role is associated with:\n %s' % ("\n".join(project_names))))
        return super(project_project_role, self).unlink(cr, uid, ids, context)
    
    def write(self, cr, uid, role_ids, values, context=None):
        """
        Override orm.write() to prohibit changing the groups if the role is still associated to some projects
        """
        if values and values.has_key('related_group_ids'):
            project_names = self.get_name_projects_associated(cr, uid, role_ids, context)
            if len(project_names) > 0:
                raise osv.except_osv(_('Operation not permitted !'), _('You can not modify roles associated to projects!\nThis role is associated with:\n%s' % ("\n".join(project_names))))
        return super(project_project_role, self).write(cr, uid, role_ids, values, context) 
        
project_project_role()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
