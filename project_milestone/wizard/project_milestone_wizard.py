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
# Created:               Mar 25, 2020 3:26:58 PM by atrabelsi
# Last modified:      2020-03-25 15:26
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import ValidationError, except_orm

class project_milestone_builder(models.TransientModel):
    
    _name = 'project.milestone'
    _description = "wizard to create project milestones as calendar event"
    
    _inherit = "calendar.event"
    
    name_pattern = fields.Char(string = 'Milestone Name Pattern')
    recurrency = fields.Boolean('Recurrent', default = True)
    
    @api.onchange('interval')
    def on_change(self):
        if not self.interval :
            self.recurrency = False
            
    @api.model
    def default_get(self, field_list):
        default = super(project_milestone_builder, self).default_get(field_list)
        if self._context and self._context.get('active_id') :
            project = self.env['project.project'].browse(self._context['active_id'])
            default['start_date'] = project.date_start
            default['stop_date'] = project.date_start
            default['allday'] = True
            default['project_id'] = project.id
            default['final_date'] = project.date
        return default
            
#     project_id = fields.Many2one('project.project',  string ='Project')
#     recurring_every = fields.Integer(string = 'Recurring Every', help = 'recurring Milestone Every Recurring Unit. If zero, the milestone is not recurring')
#     recurring_unit = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')], string = 'Recurring Unit')
#     weekdays = fields.Selection( [('mo', 'Monday'), ('tu', 'Tuesday'), ('we', 'Wednesday'), ('th', 'Thuesday'), ('fi', 'Friday'), ('sa', 'Saturday'), ('su', 'Sunday')],string="Weekdays")

    @api.model
    def create(self, vals):
        vals['name'] = vals['name_pattern']
        del vals['name_pattern']
        self.env['calendar.event'].create(vals)
        return {
                'type': 'ir.actions.act_window_close',
                }
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
