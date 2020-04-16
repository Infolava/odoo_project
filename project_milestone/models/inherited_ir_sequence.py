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
# Created:               Apr 14, 2020 11:36:48 AM by atrabelsi
# Last modified:      2020-04-14 11:36
#
# Last Author:           $LastChangedBy$
# Last Checkin:          $LastChangedDate$
# Checked out Version:   $LastChangedRevision$
# HeadURL:               $HeadURL$
# --------------------------------------------------------------------------------
from openerp import models, fields
from datetime import datetime
import pytz
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ir_sequence(models.Model):
    
    """
        Extend ir_sequene model : Force prefix date
    """
    
    _name = 'ir.sequence'
    _inherit = 'ir.sequence'
    
    def _interpolation_dict_context(self, context=None):
        # Override to force event date
        if context is None:
            context = {}
        if context.get('force_date') :
            t = datetime.strptime(context.get('force_date'), DF) 
        else :
            t = datetime.now(pytz.timezone(context.get('tz') or 'UTC'))
        sequences = {
            'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
            'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
        }
        return {key: t.strftime(sequence) for key, sequence in sequences.iteritems()}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
#eof $Id$