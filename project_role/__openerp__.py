# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------------
# Project:               TransALM
# Copyright:           © 2017 Infolava GmbH. All rights reserved.
# License:
# --------------------------------------------------------------------------------
#    This file is part of TransALM
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# --------------------------------------------------------------------------------
# Created:               25 Nov 2014 08:57:25 by atrabelsi
# Last modified:      2017-04-10 11:07:19 AM
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
{
    'name' : 'Project Roles',
    'version' : '2.1.1',
    'author' : 'Infolava',
    'website': 'http://www.infolava.ch',
    'category' : 'Project Management',
    'depends' : [
                 'project',
                 'hr_contract_work_place',
                 'hr_public_holidays',
                 'hr_holidays',
                 'project_stage_closed', # Define closed project stage
                 'hr_payroll',
                 'hr_skill'
                ],
    'demo_xml' : [],
    'summary': 'Addon to staff projects based on roles and employees contracts',
    'data' : [
              'security/ir_ui_model.xml',
              'security/ir_rule.xml',
              'wizard/employee_role_wizard.xml',
              'wizard/project_milestone_wizard.xml',
              'views/project_project_role_view.xml',
              'views/project_role_view.xml',
              'views/inherited_hr_employee_view.xml',
              'views/inherited_project_project_view.xml',
              'views/inherited_ir_rule_view.xml',
              'data/project_role_data.xml',
              'data/project_task_stage.xml',
                  ],
    'active': False,
    'installable': True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$
