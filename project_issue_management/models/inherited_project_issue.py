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
# Created:               Feb 1, 2021 12:50:14 PM by hbouzidi
# Last modified:      2021-02-01 12:50
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields, api

class project_issue(models.Model):
    """
        Extend the Project Model with project milestone
    """
    _name = 'project.issue'
    _inherit = 'project.issue'
    _description = 'Extension for project issue model'
    
    issue_ref = fields.Char('Reference', readonly = True, copy = False)
    contract_id = fields.Many2one('account.analytic.account', 'Contract', readonly = True)
    contract_ref = fields.Char(related ='contract_id.code', string ='Contract Reference', readonly = True)
    
    
    @api.model
    def create(self, vals):
        reference = {'issue_ref': self.env['ir.sequence'].get('project.issue.sequence')}
        vals.update(reference)
        return super(project_issue,self).create(vals)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$