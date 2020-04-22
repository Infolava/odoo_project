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
from openerp import models, fields

class project_milestone(models.Model):
    """
        Extend the Calendar Event Model : select project within event definition
    """
    _name = 'project.milestone'
    
    project_id = fields.Many2one('project.project', string='Project')
    event_id = fields.Many2one('calendar.event')
    date = fields.Date(related = 'event_id.start_date', string = "Date")
    name = fields.Char(related = "event_id.name", string = "Name", store = True)
    description = fields.Text('Description')
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$