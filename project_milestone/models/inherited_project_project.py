# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2020 Infolava GmbH. All rights reserved.
# License:
# --------------------------------------------------------------------------------
#    This file is part of TransALM
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# --------------------------------------------------------------------------------
# Created:               Apr 2, 2020 11:55:17 PM by atrabelsi
# Last modified:      2020-04-02 23:55
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api, _, SUPERUSER_ID
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class project_project(models.Model):
    """
        Extend the Project Model with project milestone
    """
    _name = 'project.project'
    _inherit = 'project.project'


    @api.depends('milestone_ids')
    def _count_milestone(self):
        for prj in self :
            prj.count_milestone = len(prj.milestone_ids.ids)
        
    milestone_ids = fields.One2many('project.milestone', 'project_id', string = 'Milestones')
    count_milestone = fields.Integer(compute = _count_milestone, string = "Milestones")
    
               
    @api.multi
    def action_view_tasks_milestone(self):
        self.ensure_one()
        task_project_action = self.env.ref('project.act_project_project_2_project_task_all')
        result = task_project_action.read()[0]
        if self.milestone_ids:
            current_milestone = self.milestone_ids.filtered(lambda mil : datetime.datetime.strptime(mil.date, DF) >= datetime.datetime.today())
            if current_milestone :
                result['context'] =result['context'].split('}')[0] + "'search_default_milestone_id' : %s }" % current_milestone[0].id
        return result
    
    @api.multi
    def return_milestone_view(self) :
        self.ensure_one()
        return {
            'name': _('Milestone'),
            'domain': [('project_id', '=', self.id)],
            'res_model': 'project.milestone',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'calendar,tree,form',
            'view_type': 'form',
            'context' : {'virtual_id' : False}
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$