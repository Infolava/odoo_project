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
# Created:               Mar 30, 2020 10:02:14 AM by hbouzidi
# Last modified:      2020-03-30 10:02
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------

{
    'name' : 'Project Milestones',
    'version' : '0.0.1',
    'author' : 'Infolava',
    'website': 'http://www.infolava.ch',
    'category' : 'Project Management',
    'depends' : [
                 'project',
                 'calendar',
                ],
    'demo_xml' : [],
    'summary': 'Addon to observe the progress of a project',
    'data' : [
              'wizard/project_milestone_wizard.xml',
              'views/inherited_calendar_event_view.xml',
              'views/project_milestone_view.xml',
                  ],
    'active': False,
    'installable': True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
