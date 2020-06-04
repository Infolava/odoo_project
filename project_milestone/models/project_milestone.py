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
# Created:               Apr 2, 2020 9:57:12 PM by atrabelsi
# Last modified:      2020-04-02 21:57
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api

class project_milestone(models.Model):
    """
        Extend the Calendar Event Model : select project within event definition
    """
    _name = 'project.milestone'
    _order = 'date asc'
    
    
    project_id = fields.Many2one('project.project', string='Project')
    event_id = fields.Many2one('calendar.event')
    date = fields.Date(related = 'event_id.start_date', string = "Date", store = True)
    name = fields.Char(related = "event_id.name", string = "Name", store = True)
    description = fields.Text('Description')
    
    @api.model
    def create(self,values):
        """Override create method to enable create milestone from calendar form view"""
        
        if values['event_id'] is False:
            project = self.env['project.project'].browse(values['project_id'])
            meeting_vals = {}
            meeting_vals.update({'start_date': values['date'], 'stop_date': values['date']})
            meeting_vals.update({'name': values['name']})
            meeting_vals.update({
                                 'duration': 24,
                                 'class': 'private',
                                 'allday' : True,
                                 'project_id':values['project_id'],
                                 'partner_ids' : [[6, False, [mem.partner_id.id for mem in project.members] + [project.user_id.partner_id.id]]]
                                 })
             
            values['event_id'] = self.env['calendar.event'].with_context(no_email = True).create(meeting_vals).id
        return super(project_milestone, self).create(values)

    @api.multi
    def write(self,values):
        meeting_vals = {}
        if values.get('date') :
            meeting_vals.update({'start_date': values['date'], 'stop_date': values['date']})
        if values.get('name') :
            meeting_vals.update({'name': values['name']})
        if values.get('project_id'):
            meeting_vals.update({'project_id': values['project_id']})
        self.event_id.write(meeting_vals)
        return super(project_milestone, self).write(values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$