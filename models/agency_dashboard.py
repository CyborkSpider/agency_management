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
from dateutil.relativedelta import relativedelta


class AgencyDashboard(models.TransientModel):
    _name = 'agency.dashboard'
    _description = 'Agency Dashboard Metrics'

    name = fields.Char(default="Agency Dashboard")

    def get_dashboard_data(self):
        """Returns dict of data for the JS dashboard view."""
        Project = self.env['agency.project']
        Team = self.env['agency.team']
        today = fields.Date.context_today(self)

        # -- Period boundaries ------------------------------------------------
        # Current month
        cur_start = today.replace(day=1)
        # Previous month
        prev_end = cur_start - relativedelta(days=1)
        prev_start = prev_end.replace(day=1)

        # -- Overview ---------------------------------------------------------
        active_projects = Project.search_count([('state', 'in', ['in_progress', 'review'])])
        completed_projects = Project.search_count([('state', '=', 'completed')])
        all_teams = Team.search([])
        active_teams = len(all_teams.filtered(lambda t: t.state != 'inactive'))
        available_teams = len(all_teams.filtered(lambda t: t.state == 'available'))
        overloaded_teams = len(all_teams.filtered(lambda t: t.state == 'overloaded'))

        # -- Project Risk -----------------------------------------------------
        on_track = Project.search_count([('risk_level', '=', 'on_track'), ('state', 'not in', ['completed', 'cancelled'])])
        at_risk = Project.search_count([('risk_level', '=', 'at_risk'), ('state', 'not in', ['completed', 'cancelled'])])
        overdue = Project.search_count([('risk_level', '=', 'critical'), ('state', 'not in', ['completed', 'cancelled'])])

        # -- Finance (all time, completed projects) ----------------------------
        all_completed = Project.search([('state', '=', 'completed')])
        revenue = sum(all_completed.mapped('revenue'))
        cost = sum(all_completed.mapped('cost'))
        profit = sum(all_completed.mapped('gross_profit'))
        margin = round((profit / revenue * 100), 1) if revenue > 0 else 0.0

        # -- Growth: current month vs previous month ---------------------------
        def _period_stats(start, end):
            projects = Project.search([
                ('state', '=', 'completed'),
                ('date_deadline', '>=', start),
                ('date_deadline', '<=', end),
            ])
            rev = sum(projects.mapped('revenue'))
            prof = sum(projects.mapped('gross_profit'))
            return {
                'count': len(projects),
                'revenue': rev,
                'profit': prof,
            }

        cur = _period_stats(cur_start, today)
        prev = _period_stats(prev_start, prev_end)

        def _growth(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100, 1)

        growth = {
            'revenue': _growth(cur['revenue'], prev['revenue']),
            'profit': _growth(cur['profit'], prev['profit']),
            'projects': _growth(cur['count'], prev['count']),
        }

        # -- New clients this month --------------------------------------------
        clients_cur = len(Project.search([
            ('date_start', '>=', cur_start), ('date_start', '<=', today)
        ]).mapped('client_id'))
        clients_prev = len(Project.search([
            ('date_start', '>=', prev_start), ('date_start', '<=', prev_end)
        ]).mapped('client_id'))
        growth['clients'] = _growth(clients_cur, clients_prev)

        return {
            'overview': {
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'active_teams': active_teams,
                'available_teams': available_teams,
                'overloaded_teams': overloaded_teams,
            },
            'projects': {
                'on_track': on_track,
                'at_risk': at_risk,
                'overdue': overdue,
            },
            'finance': {
                'revenue': revenue,
                'cost': cost,
                'profit': profit,
                'margin': margin,
            },
            'growth': growth,
            'period': {
                'current_month': cur_start.strftime('%B %Y'),
                'previous_month': prev_start.strftime('%B %Y'),
            },
        }
