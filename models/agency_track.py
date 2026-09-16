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
from odoo import api, fields, models


class AgencyTrack(models.Model):
    _name = 'agency.track'
    _description = 'Agency Track / Specialization'
    _order = 'sequence, name'

    name = fields.Char(string='Track Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )

    # Relations
    team_ids = fields.One2many('agency.team', 'track_id', string='Teams')
    team_count = fields.Integer(
        string='Team Count', compute='_compute_team_count',
    )

    @api.depends('team_ids')
    def _compute_team_count(self):
        for track in self:
            track.team_count = len(track.team_ids)

    def action_view_teams(self):
        """Smart button to view teams in this track."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Teams â€” {self.name}',
            'res_model': 'agency.team',
            'view_mode': 'list,form,kanban',
            'domain': [('track_id', '=', self.id)],
            'context': {'default_track_id': self.id},
        }
