# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM SaaS
# Copyright:           © 2021 Infolava GmbH. All rights reserved.
# License:
# --------------------------------------------------------------------------------
#    This file is part of TransALM Saas
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# --------------------------------------------------------------------------------
# Created:               Feb 1, 2021 12:27:38 PM by hbouzidi
# Last modified:      2021-02-01 12:27
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
{
    'name' : 'Project Issues',
    'version' : '0.0.1',
    'author' : 'Infolava',
    'website': 'http://www.infolava.ch',
    'category' : 'Project Management',
    'depends' : [
                 'project_issue',
                 #'analytic'
                ],
    'demo_xml' : [],
    'summary': 'Extension for project issue model in order to create tickets based on customer contracts',
    'data' : ['data/project_issue_sequence.xml',
              'views/inherited_project_issue_view.xml'
              ],
    'active': False,
    'installable': True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$