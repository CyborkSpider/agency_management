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


class AgencyProjectRating(models.Model):
    _name = 'agency.project.rating'
    _description = 'Agency Project Rating'
    _order = 'date desc, id desc'

    agency_project_id = fields.Many2one(
        'agency.project', string='Project',
        required=True, ondelete='cascade', index=True
    )
    team_id = fields.Many2one(
        'agency.team', string='Rated Team',
        required=True, index=True
    )

    # -- Rating Dimensions -----------------------------------------------------
    client_rating = fields.Float(
        string='Client Satisfaction (1-5)', required=True, default=5.0,
        help="Client overall satisfaction rating from 1 (worst) to 5 (best)."
    )
    quality_score = fields.Float(
        string='Quality Score (0-100)', required=True, default=100.0,
        help="Rate the quality of deliverables from 0 to 100."
    )
    on_time_score = fields.Float(
        string='On-Time Delivery (0-100)', required=True, default=100.0,
        help="Rate the timeliness of delivery from 0 to 100."
    )
    communication_score = fields.Float(
        string='Communication Score (0-100)', required=True, default=100.0,
        help="Rate the team communication and responsiveness from 0 to 100."
    )

    # -- Derived ---------------------------------------------------------------
    overall_score = fields.Float(
        string='Overall Score (0-100)',
        compute='_compute_overall_score', store=True,
        help=(
            "Weighted overall score:\n"
            "  35% Client Satisfaction (converted to 0-100)\n"
            "  25% Quality\n"
            "  25% On-Time Delivery\n"
            "  15% Communication"
        )
    )

    comments = fields.Text(string='Client Comments')
    rated_by = fields.Many2one(
        'res.users', string='Rated By',
        default=lambda self: self.env.user
    )
    date = fields.Date(
        string='Rating Date', default=fields.Date.context_today, required=True
    )

    @api.depends('client_rating', 'quality_score', 'on_time_score', 'communication_score')
    def _compute_overall_score(self):
        for rating in self:
            # Convert client_rating (1-5) to 0-100 scale
            client_100 = ((rating.client_rating - 1) / 4.0) * 100 if rating.client_rating >= 1 else 0.0

            # Clamp all scores to valid ranges
            quality = max(0.0, min(rating.quality_score, 100.0))
            on_time = max(0.0, min(rating.on_time_score, 100.0))
            communication = max(0.0, min(rating.communication_score, 100.0))
            client_clamped = max(0.0, min(client_100, 100.0))

            # Weighted formula
            rating.overall_score = (
                client_clamped    * 0.35 +
                quality           * 0.25 +
                on_time           * 0.25 +
                communication     * 0.15
            )
