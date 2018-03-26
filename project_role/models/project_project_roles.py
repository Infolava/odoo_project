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

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm

class project_project_role(models.Model):
    
    _name = 'project.project.roles'
    _description = 'Define and specify software project roles'
    _rec_name = 'role_name'
    
    role_name = fields.Char(string = 'Name', required = True, translate = True)
    description = fields.Char(string = 'Description', translate = True)
    related_group_ids = fields.Many2many('res.groups', rel = 'project_roles_groups_rel', string = 'Groups', required = True)

    _sql_constraints = [
                        ('unique_role_name', 'UNIQUE (role_name)', _('Role already exists!')),
                        ]
    
    @api.model
    def create(self, values):
        if values.get('related_group_ids') == [[6, False, []]] or not values['related_group_ids']:
            raise ValidationError(_('Please Choose a related group to the role'))
        role_ids = self.sudo().search([('related_group_ids', 'in', values['related_group_ids'][0][2])])
        for role in role_ids :
            if role.related_group_ids.ids == values['related_group_ids'][0][2] :
                raise ValidationError(_('A role with the same groups exists already!'))
        return super(project_project_role, self).create(values)
    
    @api.multi
    def get_name_projects_associated(self):
        """
        Finds projects associated with role
        :param role_ids
        :return list of string with names of the associated projects
        """
        projects = self.env['project.project'].search([('project_role_ids.id', 'in', self._ids)])
        return [prj.name for prj in projects]
    
    @api.multi
    def unlink(self):
        """
        Override orm.unlink() to prohibit deleting roles that are associated to some projects
        """
        project_names = self.get_name_projects_associated()
        if project_names:
            raise except_orm(_('Operation not permitted !'), _('You can not delete roles associated to projects!\nThis role is associated with:\n %s' % ("\n".join(project_names))))
        return super(project_project_role, self).unlink()
    
    @api.multi
    def write(self, values):
        """
        Override orm.write() to prohibit changing the groups if the role is still associated to some projects
        """
        if values.get('related_group_ids'):
            project_names = self.get_name_projects_associated()
            if project_names :
                raise except_orm(_('Operation not permitted !'), _('You can not modify roles associated to projects!\nThis role is associated with:\n%s' % ("\n".join(project_names))))
        return super(project_project_role, self).write(values) 
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
