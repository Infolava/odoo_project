# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2018 Infolava GmbH. All rights reserved.
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
# Created:               Jan 24, 2018 10:12:25 AM by atrabelsi
# Last modified:      2018-01-24 10:12
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
{
    'name' : 'Field Domain By Group',
    'version' : '2.1.0',
    'author' : 'TransProg S.A.R.L',
    'website': 'http://www.transprog.com',
    "category": "Hidden/Dependency",
    'depends' : [
                 'base',
                ],
    'summary': 'Specify field domain by user group',
    'data' : [
              'ir_field_rule_view.xml',
                  ],
    'active': False,
    'installable': True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$