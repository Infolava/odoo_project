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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import time

def calendar_id2real_id(calendar_id=None, with_date=False):
    """
    Convert a "virtual/recurring event id" (type string) into a real event id (type int).
    E.g. virtual/recurring event id is 4-20091201100000, so it will return 4.
    @param calendar_id: id of calendar
    @param with_date: if a value is passed to this param it will return dates based on value of withdate + calendar_id
    @return: real event id
    """
    if calendar_id and isinstance(calendar_id, (basestring)):
        res = calendar_id.split('-')
        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT, time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            return int(real_id)
    return calendar_id and int(calendar_id) or calendar_id


class project_milestone_builder(models.TransientModel):
    
    _name = 'project.milestone.builder'
    _description = "wizard to create project milestones as calendar event"
    
    _inherits = { "calendar.event" : 'event_id'}
    
    event_id = fields.Many2one('calendar.event', 'Event', required = True, ondelete="cascade")
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
# 
    @api.model
    def create(self, vals):
        vals['name'] = vals['name_pattern']
#         vals['message_follower_ids'] = [[6, False, []]]
#         vals['message_is_follower'] = False
#         vals['partner_ids'] = [[6, False, []]]
        del vals['name_pattern']
        res = self.env['calendar.event'].create(vals)
        vals['event_id'] = res.id
        return super(project_milestone_builder, self).create(vals)
#         
    @api.multi
    def create_milestone(self):
        #events = self.event_id.get_recurrent_ids([])
        #events = self.pool.get('calendar.event').get_recurrent_ids(self._cr, self._uid, self.event_id.id, ['&', ['start', '>=', self.event_id.start_date], ['stop', '<=', self.event_id.final_date]])
        events = self.event_id.search(['&',['id', '=', self.event_id.id], '&', ['start', '>=', self.event_id.start_date], ['stop', '<=', self.event_id.final_date]])
        
        i = 0
        for event in events :
            i += 1
            new_ev = event._detach_one_event({'name' : event.name + str(i)})
            self.env['project.milestone'].create({'project_id' : self.project_id.id, 'event_id' : new_ev[0]})
        return {
                'type': 'ir.actions.act_window_close',
                }
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
