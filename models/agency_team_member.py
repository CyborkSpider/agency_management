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


class AgencyTeamMember(models.Model):
    _name = 'agency.team.member'
    _description = 'Agency Team Member'
    _order = 'role desc, id'
    _rec_name = 'employee_id'

    team_id = fields.Many2one(
        'agency.team', string='Team',
        required=True, ondelete='cascade', index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        required=True, index=True,
    )
    role = fields.Selection([
        ('member', 'Member'),
        ('senior', 'Senior'),
        ('lead', 'Team Lead'),
    ], string='Role', default='member', required=True)
    join_date = fields.Date(
        string='Join Date', default=fields.Date.context_today,
    )
    is_active = fields.Boolean(string='Active', default=True)

    # Direct writable skills stored at the member level
    skill_ids = fields.Many2many(
        'hr.skill',
        'agency_team_member_skill_rel',
        'member_id',
        'skill_id',
        string='Skills',
        help='Skills of this member within the team context.',
    )

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Suggest employee HR skills when employee is selected."""
        if self.employee_id and not self.skill_ids:
            employee_skills = self.employee_id.employee_skill_ids.mapped('skill_id')
            if employee_skills:
                self.skill_ids = employee_skills

    _sql_constraints = [
        ('employee_team_unique',
         'UNIQUE(team_id, employee_id)',
         'An employee can only be a member of a team once.'),
    ]
