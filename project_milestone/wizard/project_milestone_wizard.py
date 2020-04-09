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
from openerp import models, fields, api, _



class project_milestone_builder(models.TransientModel):
    
    _name = 'project.milestone.builder'
    _description = "wizard to create project milestones as calendar event"
    
    _inherits = { "calendar.event" : 'event_id',
                 'ir.sequence' : 'sequence_id'}
    
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', required = True, ondelete="cascade")
    event_id = fields.Many2one('calendar.event', 'Event', required = True, ondelete="cascade")
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
            
# 
    @api.model
    def create(self, vals):
        vals['name'] = 'milestone.sequence'
        vals['event_id'] = self.env['calendar.event'].create(vals).id
        vals['code'] = 'milestone.sequence'
        vals['sequence_id'] = self.env['ir.sequence'].create(vals).id
        return super(project_milestone_builder, self).create(vals)
#         
    @api.multi
    def create_milestone(self):
        events = self.event_id.search(['&',['id', '=', self.event_id.id], '&', ['start', '>=', self.event_id.start_date], ['stop', '<=', self.event_id.final_date]], order = 'start_date asc')
        
        for event in events :
            new_name = self.pool.get('ir.sequence').next_by_id(self._cr, self._uid, self.sequence_id.id)
            new_ev = event._detach_one_event({'name' : new_name})
            self.env['project.milestone'].create({'project_id' : self.project_id.id, 'event_id' : new_ev[0]})
        return {
                'type': 'ir.actions.act_window_close',
                }
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
