# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2020 All rights reserved.
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
# Created:               Apr 9, 2020 11:58:38 AM by hbouzidi
# Last modified:      2020-04-09 11:58
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import except_orm, ValidationError
from datetime import date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class project_task(models.Model):
    """
    """
    _name = 'project.task'
    _inherit = 'project.task'
    
       
    @api.depends('date_deadline', 'date_start', 'project_id', 'stage_id', 'project_id.milestone_ids')
    def _get_milestones(self):
        for task in self :
            task.milestone_ids = [[6, False, []]]
            task.milestone_id = False
            domain = []
            if task.project_id :
                domain = [('project_id', '=', task.project_id.id)]
                if task.date_start :
                    domain.append(('date', '>=', fields.Datetime.from_string(task.date_start).date()))
                domain_prev = domain[:]
                task.date_deadline = task.date_deadline if task.date_deadline else task.project_id.date
                if fields.Date.from_string(task.date_deadline) >= date.today() :
                    domain.append(('date', '>=', date.today()))
                    domain_prev.append(('date', '<' , date.today()))
                    milestones = self.env['project.milestone'].search(domain, order="date asc")
                    prev_mil = self.env['project.milestone'].search(domain_prev, order="date asc").ids
                    if milestones :
                        if task.stage_id not in task.project_id.type_ids.filtered(lambda x : x.closed) :
                            
                            task.milestone_id = milestones.ids[0]
                            
                        else :
                            task.milestone_ids = [[6, False, prev_mil+ [milestones.ids[0]]]]
                    else :
                        task.milestone_ids = [[6, False, prev_mil]]
                else :
                    domain_prev.append(('date', '<' , task.date_deadline))
                    task.milestone_ids =  [[6, False, self.env['project.milestone'].search(domain_prev, order = "date asc").ids]]


    
    milestone_ids = fields.Many2many('project.milestone', 'project_task_milestone_rel','milestone','task',compute = _get_milestones, string = 'Previous Milestones', readonly=True, store = True)
    milestone_id = fields.Many2one('project.milestone', compute = _get_milestones, string = 'Current Milestone', store = True)
    
