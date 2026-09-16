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
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AgencyAssignWizard(models.TransientModel):
    _name = 'agency.assign.wizard'
    _description = 'Manual Assignment Override'

    project_id = fields.Many2one(
        'agency.project', string='Project', required=True,
        default=lambda self: (
            self.env['agency.project'].browse(self.env.context.get('active_id'))
            if self.env.context.get('active_model') == 'agency.project'
            else self.env.context.get('default_project_id', False)
        )
    )
    team_id = fields.Many2one('agency.team', string='Team to Assign', required=True)
    reason = fields.Text(string='Override Reason', required=True)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            return {'domain': {'team_id': [('track_id', '=', self.project_id.track_id.id)]}}

    def action_assign(self):
        self.ensure_one()

        if self.project_id.state not in ['draft', 'pending_assignment', 'assigned']:
            raise UserError(_("Cannot re-assign a project that is already in progress or completed."))

        previous_team = self.project_id.assigned_team_id

        self.project_id.write({
            'assigned_team_id': self.team_id.id,
            'assignment_reason': f"MANUAL OVERRIDE: {self.reason}",
            'assignment_date': fields.Datetime.now(),
            'assignment_score': 0.0,
            'state': 'assigned',
        })

        self.env['agency.assignment.history'].create({
            'agency_project_id': self.project_id.id,
            'team_id': self.team_id.id,
            'previous_team_id': previous_team.id if previous_team else False,
            'score': 0.0,
            'reason': f"MANUAL OVERRIDE: {self.reason}",
            'assigned_by': self.env.user.id,
            'is_auto': False
        })

        self.project_id.message_post(
            body=f"Manually assigned to team {self.team_id.name}. Reason: {self.reason}"
        )
        return {'type': 'ir.actions.act_window_close'}
