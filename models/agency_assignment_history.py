# =============================================================================
#
#   AGENCY MANAGEMENT MODULE — Freelancing Agency System for Odoo 19
#
#   Lead Developer & Architect:
#       Ziad Elgohary
#       Portfolio : https://cyborkspider.github.io/en/
#
#   Contributing Developer:
#       Omar Bahnasy
#
#   © 2026 Ziad Elgohary & Omar Bahnasy. All rights reserved.
#   This source code is proprietary. Unauthorised copying, modification,
#   redistribution, or use — in whole or in part — without the explicit
#   written permission of the lead developer is strictly prohibited.
#
# =============================================================================
from odoo import fields, models


class AgencyAssignmentHistory(models.Model):
    _name = 'agency.assignment.history'
    _description = 'Agency Assignment History'
    _order = 'date desc, id desc'

    agency_project_id = fields.Many2one(
        'agency.project', string='Project',
        required=True, ondelete='cascade', index=True
    )
    team_id = fields.Many2one(
        'agency.team', string='Assigned Team',
        required=True, index=True
    )
    previous_team_id = fields.Many2one(
        'agency.team', string='Previous Team'
    )
    score = fields.Float(string='Assignment Score')
    reason = fields.Text(string='Reason')
    date = fields.Datetime(
        string='Date', default=fields.Datetime.now, required=True
    )
    assigned_by = fields.Many2one(
        'res.users', string='Assigned By',
        default=lambda self: self.env.user
    )
    is_auto = fields.Boolean(string='Auto Assigned')
