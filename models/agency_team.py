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


class AgencyTeam(models.Model):
    _name = 'agency.team'
    _description = 'Agency Team'
    _order = 'name'

    name = fields.Char(string='Team Name', required=True)
    code = fields.Char(
        string='Code', required=True, copy=False, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agency.team') or 'New'
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color')

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )

    track_id = fields.Many2one(
        'agency.track', string='Track/Specialization', required=True,
        domain="[('active', '=', True)]",
    )
    manager_id = fields.Many2one(
        'hr.employee', string='Team Manager', required=True,
        domain="[('company_id', '=', company_id)]",
    )

    member_ids = fields.One2many(
        'agency.team.member', 'team_id', string='Members',
    )
    member_count = fields.Integer(
        string='Member Count', compute='_compute_member_count',
    )

    # Aggregated skills from all member records (stored on member, pulled here)
    skill_ids = fields.Many2many(
        'hr.skill', string='Team Skills',
        compute='_compute_skill_ids', store=True,
    )

    # Capacity and Workload
    capacity = fields.Integer(
        string='Capacity (Projects)', required=True, default=3,
        help="Maximum number of active projects this team can handle at once."
    )
    current_load = fields.Integer(
        string='Current Load', compute='_compute_load', store=False,
    )
    availability = fields.Float(
        string='Availability (%)', compute='_compute_load', store=False,
    )
    state = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('overloaded', 'Overloaded'),
        ('inactive', 'Inactive'),
    ], string='Status', compute='_compute_state', store=False)

    # Financial Rates
    internal_rate = fields.Monetary(
        string='Internal Rate / Hour', currency_field='currency_id',
        default=15.0, help="Internal cost per hour for this team."
    )
    billing_rate = fields.Monetary(
        string='Billing Rate / Hour', currency_field='currency_id',
        default=40.0, help="Amount billed to client per hour."
    )

    # Projects & Ratings
    project_ids = fields.One2many(
        'agency.project', 'assigned_team_id', string='Projects'
    )
    agency_rating_ids = fields.One2many(
        'agency.project.rating', 'team_id', string='Ratings'
    )

    # -- Performance fields — store=True so they persist & dashboard can aggregate --
    rating_avg = fields.Float(
        string='Avg Client Rating (1-5)',
        compute='_compute_performance', store=True,
        help="Average client satisfaction rating (1-5) across all project ratings."
    )
    on_time_rate = fields.Float(
        string='On-Time Delivery %',
        compute='_compute_performance', store=True,
        help="Average on-time delivery score across all project ratings."
    )
    performance_score = fields.Float(
        string='Performance Score (0-100)',
        compute='_compute_performance', store=True,
        help="Weighted performance score derived from project ratings."
    )

    # -- Team-level financial aggregates from completed projects ---------------
    total_revenue = fields.Monetary(
        string='Total Revenue', currency_field='currency_id',
        compute='_compute_team_financials', store=True,
        help="Sum of revenue (client budgets) from all completed projects."
    )
    total_cost = fields.Monetary(
        string='Total Cost', currency_field='currency_id',
        compute='_compute_team_financials', store=True,
    )
    total_profit = fields.Monetary(
        string='Total Profit', currency_field='currency_id',
        compute='_compute_team_financials', store=True,
    )
    avg_margin = fields.Float(
        string='Avg Margin (%)',
        compute='_compute_team_financials', store=True,
        help="(Total Profit / Total Revenue) x 100"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('agency.team') or 'New'
        return super().create(vals_list)

    @api.depends('member_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)

    @api.depends('member_ids.skill_ids')
    def _compute_skill_ids(self):
        for team in self:
            skills = self.env['hr.skill']
            for member in team.member_ids:
                skills |= member.skill_ids
            team.skill_ids = skills

    def _compute_load(self):
        for team in self:
            active_projects = self.env['agency.project'].search_count([
                ('assigned_team_id', '=', team.id),
                ('state', 'in', ['assigned', 'in_progress', 'review'])
            ])
            team.current_load = active_projects

            if team.capacity > 0:
                available = ((team.capacity - active_projects) / team.capacity) * 100
                team.availability = max(0.0, available)
            else:
                team.availability = 0.0

    @api.depends('capacity', 'current_load', 'active')
    def _compute_state(self):
        for team in self:
            if not team.active:
                team.state = 'inactive'
            elif team.current_load >= team.capacity:
                team.state = 'overloaded'
            elif team.current_load > 0:
                team.state = 'busy'
            else:
                team.state = 'available'

    @api.depends(
        'agency_rating_ids',
        'agency_rating_ids.overall_score',
        'agency_rating_ids.client_rating',
        'agency_rating_ids.on_time_score',
        'agency_rating_ids.quality_score',
        'agency_rating_ids.communication_score',
    )
    def _compute_performance(self):
        for team in self:
            ratings = team.agency_rating_ids
            if not ratings:
                team.rating_avg = 0.0
                team.on_time_rate = 0.0
                team.performance_score = 0.0
                continue

            count = len(ratings)
            team.rating_avg = sum(ratings.mapped('client_rating')) / count
            team.on_time_rate = sum(ratings.mapped('on_time_score')) / count

            # performance_score = average of overall_score (already weighted in rating model)
            team.performance_score = sum(ratings.mapped('overall_score')) / count

    @api.depends(
        'project_ids',
        'project_ids.state',
        'project_ids.revenue',
        'project_ids.cost',
        'project_ids.gross_profit',
    )
    def _compute_team_financials(self):
        for team in self:
            completed = team.project_ids.filtered(lambda p: p.state == 'completed')
            if not completed:
                team.total_revenue = 0.0
                team.total_cost = 0.0
                team.total_profit = 0.0
                team.avg_margin = 0.0
                continue

            team.total_revenue = sum(completed.mapped('revenue'))
            team.total_cost = sum(completed.mapped('cost'))
            team.total_profit = sum(completed.mapped('gross_profit'))
            if team.total_revenue > 0:
                team.avg_margin = (team.total_profit / team.total_revenue) * 100
            else:
                team.avg_margin = 0.0

    def action_view_projects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects - {self.name}',
            'res_model': 'agency.project',
            'view_mode': 'list,form',
            'domain': [('assigned_team_id', '=', self.id)],
            'context': {'default_assigned_team_id': self.id},
        }

    def action_view_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Members - {self.name}',
            'res_model': 'agency.team.member',
            'view_mode': 'list,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id},
        }
