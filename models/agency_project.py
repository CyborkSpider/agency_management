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


class AgencyProject(models.Model):
    _name = 'agency.project'
    _description = 'Agency Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_deadline, id desc'

    name = fields.Char(string='Project Name', required=True, tracking=True)
    code = fields.Char(
        string='Project Code', required=True, copy=False, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('agency.project') or 'New'
    )

    # Linked entities
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)

    # Requirements
    track_id = fields.Many2one('agency.track', string='Required Track', required=True, tracking=True)
    required_skill_ids = fields.Many2many('hr.skill', string='Required Skills')
    required_team_size = fields.Integer(string='Min Team Size', default=1)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)

    # Dates & Effort
    date_start = fields.Date(string='Start Date', default=fields.Date.context_today, required=True, tracking=True)
    date_deadline = fields.Date(string='Deadline', required=True, tracking=True)
    estimated_hours = fields.Float(string='Estimated Hours', required=True, tracking=True)

    # Assignment
    assigned_team_id = fields.Many2one('agency.team', string='Assigned Team', tracking=True, readonly=True)
    assignment_score = fields.Float(string='Assignment Score', readonly=True)
    assignment_date = fields.Datetime(string='Assignment Date', readonly=True)
    assignment_reason = fields.Text(string='Assignment Reason', readonly=True)
    assignment_history_ids = fields.One2many('agency.assignment.history', 'agency_project_id', string='Assignment History')

    # Odoo standard links
    project_id = fields.Many2one('project.project', string='Odoo Project', readonly=True, copy=False)

    # --- Financials -----------------------------------------------------------
    # Revenue = Client Budget / Contract Value (single source of truth)
    budget = fields.Monetary(
        string='Client Budget / Contract Value',
        currency_field='currency_id', tracking=True,
        help="The agreed contract value with the client. This is the project revenue."
    )

    # Team rates (read from team, used for cost calculation)
    billing_rate = fields.Monetary(related='assigned_team_id.billing_rate', string='Team Billing Rate')
    internal_rate = fields.Monetary(related='assigned_team_id.internal_rate', string='Team Internal Rate')

    # Hours
    actual_hours = fields.Float(
        string='Actual Hours',
        compute='_compute_hours_and_financials', store=True,
    )
    hours_variance = fields.Float(
        string='Hours Variance (Estimated - Actual)',
        compute='_compute_hours_and_financials', store=True,
    )

    # Core financials — all stored=True for dashboard aggregation & SQL filtering
    revenue = fields.Monetary(
        string='Revenue',
        compute='_compute_hours_and_financials', store=True,
        currency_field='currency_id',
        help="Revenue = Client Budget (Contract Value). Not calculated from hours."
    )
    cost = fields.Monetary(
        string='Project Cost',
        compute='_compute_hours_and_financials', store=True,
        currency_field='currency_id',
        help="Cost = Actual Hours x Internal Rate. Falls back to Estimated Hours x Internal Rate."
    )
    gross_profit = fields.Monetary(
        string='Gross Profit',
        compute='_compute_hours_and_financials', store=True,
        currency_field='currency_id',
        help="Gross Profit = Revenue - Cost"
    )
    profit_margin = fields.Float(
        string='Margin (%)',
        compute='_compute_hours_and_financials', store=True,
        help="Margin % = (Gross Profit / Revenue) x 100"
    )
    # -------------------------------------------------------------------------

    # Progress & Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_assignment', 'Pending Assignment'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    deadline_status = fields.Selection([
        ('normal', 'Normal'),
        ('upcoming', 'Upcoming'),
        ('due_soon', 'Due Soon'),
        ('due_tomorrow', 'Due Tomorrow'),
        ('due_today', 'Due Today'),
        ('overdue', 'Overdue')
    ], string='Deadline Status', compute='_compute_deadline_status', store=True)

    progress = fields.Float(string='Progress (%)', compute='_compute_progress', store=False)
    risk_level = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('critical', 'Critical')
    ], string='Risk Level', compute='_compute_risk_level', store=True)

    agency_rating_ids = fields.One2many('agency.project.rating', 'agency_project_id', string='Ratings')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('agency.project') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'pending_assignment'})

    def action_auto_assign(self):
        """ The Automatic Assignment Engine """
        for project in self:
            if project.state != 'pending_assignment':
                raise UserError(_("Project must be in 'Pending Assignment' state to auto-assign."))

            # Step 1: Filter teams by track — filter inactive via Python (state is not stored)
            domain = [('track_id', '=', project.track_id.id)]
            teams = self.env['agency.team'].search(domain).filtered(lambda t: t.state != 'inactive')

            if not teams:
                raise UserError(_("No active teams found for track %s.", project.track_id.name))

            best_team = None
            best_score = -1.0
            best_reason = ""

            # Step 2 & 3: Score each team
            for team in teams:
                # 1. Skill Match (25%)
                required_skills = set(project.required_skill_ids.ids)
                team_skills = set(team.skill_ids.ids)
                skill_match_pct = 0.0
                if required_skills:
                    match_count = len(required_skills.intersection(team_skills))
                    skill_match_pct = (match_count / len(required_skills)) * 100
                else:
                    skill_match_pct = 100.0

                skill_score = skill_match_pct * 0.25

                # 2. Availability (25%)
                avail_score = team.availability * 0.25

                # 3. Capacity (20%)
                cap_remaining = max(0, team.capacity - team.current_load)
                cap_pct = (cap_remaining / team.capacity * 100) if team.capacity > 0 else 0
                cap_score = cap_pct * 0.20

                # 4. Rating (15%)
                rating_score = team.performance_score * 0.15

                # 5. On-Time Rate (10%)
                delivery_score = team.on_time_rate * 0.10

                # 6. Cost Efficiency (5%) — lower internal rate is more cost-effective
                # Normalise: if billing_rate>0, margin pct as proxy for efficiency
                if team.billing_rate > 0:
                    cost_eff = ((team.billing_rate - team.internal_rate) / team.billing_rate) * 100
                else:
                    cost_eff = 0.0
                cost_score = max(0.0, min(cost_eff, 100.0)) * 0.05

                total_score = skill_score + avail_score + cap_score + rating_score + delivery_score + cost_score

                # Penalty: overloaded team
                if team.state == 'overloaded':
                    total_score -= 50

                # Penalty: team size too small
                active_members = team.member_ids.filtered(lambda m: m.is_active)
                if len(active_members) < project.required_team_size:
                    total_score -= 100

                if total_score > best_score:
                    best_score = total_score
                    best_team = team
                    best_reason = (
                        f"Score: {total_score:.2f}%\n"
                        f"Skill Match: {skill_score:.2f}/25\n"
                        f"Availability: {avail_score:.2f}/25\n"
                        f"Capacity: {cap_score:.2f}/20\n"
                        f"Rating: {rating_score:.2f}/15\n"
                        f"Delivery: {delivery_score:.2f}/10\n"
                        f"Cost Eff: {cost_score:.2f}/5"
                    )

            if not best_team:
                raise UserError(_("No team meets the minimum requirements (e.g. team size)."))

            # Step 5: Assign
            previous_team = project.assigned_team_id
            project.write({
                'assigned_team_id': best_team.id,
                'assignment_score': best_score,
                'assignment_date': fields.Datetime.now(),
                'assignment_reason': best_reason,
                'state': 'assigned'
            })

            # Log history
            self.env['agency.assignment.history'].create({
                'agency_project_id': project.id,
                'team_id': best_team.id,
                'previous_team_id': previous_team.id if previous_team else False,
                'score': best_score,
                'reason': best_reason,
                'assigned_by': self.env.user.id,
                'is_auto': True
            })

            project.message_post(body=f"Auto-assigned to team {best_team.name} with score {best_score:.2f}%.")

    def action_start(self):
        for project in self:
            if not project.assigned_team_id:
                raise UserError(_("Please assign a team first."))

            if not project.project_id:
                odoo_project = self.env['project.project'].create({
                    'name': f"{project.code} - {project.name}",
                    'partner_id': project.client_id.id,
                    'company_id': project.company_id.id,
                    'user_id': project.assigned_team_id.manager_id.user_id.id,
                    'date_start': project.date_start,
                    'date': project.date_deadline,
                })
                project.project_id = odoo_project.id

            project.state = 'in_progress'

    def action_review(self):
        self.write({'state': 'review'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_add_rating(self):
        """Open the rating creation form pre-filled with project and team."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Client Rating',
            'res_model': 'agency.project.rating',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_agency_project_id': self.id,
                'default_team_id': self.assigned_team_id.id,
            },
        }

    def action_override_assign(self):
        """Open the Override Assignment wizard pre-filled with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Override Assignment',
            'res_model': 'agency.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
            },
        }

    def action_view_odoo_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
        }

    def action_view_timesheets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Timesheets',
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.project_id.id)],
            'context': {'default_project_id': self.project_id.id},
        }

    @api.depends(
        'budget',
        'estimated_hours',
        'project_id',
        'assigned_team_id',
        'assigned_team_id.internal_rate',
        'assigned_team_id.billing_rate',
    )
    def _compute_hours_and_financials(self):
        for project in self:
            # -- Actual hours from timesheets ----------------------------------
            if project.project_id:
                timesheets = self.env['account.analytic.line'].search([
                    ('project_id', '=', project.project_id.id)
                ])
                actual_hours = sum(timesheets.mapped('unit_amount'))
            else:
                actual_hours = 0.0

            project.actual_hours = actual_hours
            project.hours_variance = project.estimated_hours - actual_hours

            # -- Revenue = Client Budget / Contract Value -----------------------
            # Revenue is NOT hours x billing_rate.
            # The client budget IS the contract value / revenue.
            project.revenue = project.budget or 0.0

            # -- Cost = Labour cost from timesheets ----------------------------
            # Fallback to estimated hours if no timesheets logged yet.
            internal_rate = project.assigned_team_id.internal_rate if project.assigned_team_id else 0.0
            hours_for_cost = actual_hours if actual_hours > 0 else project.estimated_hours
            project.cost = hours_for_cost * internal_rate

            # -- Profit & Margin -----------------------------------------------
            project.gross_profit = project.revenue - project.cost
            if project.revenue > 0:
                project.profit_margin = (project.gross_profit / project.revenue) * 100
            else:
                project.profit_margin = 0.0

    @api.depends('project_id')
    def _compute_progress(self):
        for project in self:
            if project.project_id:
                tasks = self.env['project.task'].search([('project_id', '=', project.project_id.id)])
                if tasks:
                    done_tasks = tasks.filtered(lambda t: t.state in ['1_done', '1_canceled'] or t.is_closed)
                    project.progress = (len(done_tasks) / len(tasks)) * 100
                else:
                    project.progress = 0.0
            else:
                project.progress = 0.0

    @api.depends('date_deadline', 'state')
    def _compute_deadline_status(self):
        today = fields.Date.context_today(self)
        for project in self:
            if not project.date_deadline or project.state in ['completed', 'cancelled']:
                project.deadline_status = 'normal'
                continue

            delta = (project.date_deadline - today).days

            if delta < 0:
                project.deadline_status = 'overdue'
            elif delta == 0:
                project.deadline_status = 'due_today'
            elif delta == 1:
                project.deadline_status = 'due_tomorrow'
            elif delta <= 3:
                project.deadline_status = 'due_soon'
            elif delta <= 7:
                project.deadline_status = 'upcoming'
            else:
                project.deadline_status = 'normal'

    @api.depends('deadline_status', 'progress', 'state')
    def _compute_risk_level(self):
        for project in self:
            if project.state in ['completed', 'cancelled']:
                project.risk_level = 'on_track'
                continue

            if project.deadline_status == 'overdue':
                project.risk_level = 'critical'
            elif project.deadline_status in ['due_today', 'due_tomorrow', 'due_soon'] and project.progress < 80.0:
                project.risk_level = 'at_risk'
            elif project.deadline_status == 'upcoming' and project.progress < 50.0:
                project.risk_level = 'at_risk'
            else:
                project.risk_level = 'on_track'

    @api.model
    def _cron_monitor_deadlines(self):
        """Scheduled action to monitor deadlines and generate alerts."""
        projects = self.search([('state', 'not in', ['completed', 'cancelled'])])
        projects._compute_deadline_status()
        projects._compute_risk_level()

        for project in projects:
            if project.risk_level == 'critical':
                project.message_post(
                    body=_("CRITICAL ALERT: Project is overdue!"),
                    subject=_("Overdue Project"),
                    subtype_xmlid="mail.mt_note",
                )
            elif project.risk_level == 'at_risk':
                project.message_post(
                    body=_("WARNING: Project is at risk. Deadline approaches and progress is low (%(prog)s%%).",
                           prog=round(project.progress, 1)),
                    subject=_("Project at Risk"),
                    subtype_xmlid="mail.mt_note",
                )

