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
{
    'name': 'Agency Management',
    'version': '19.0.1.0.0',
    'category': 'Services/Agency',
    'sequence': 40,
    'summary': 'Agency & Freelance ERP with Auto Team Assignment',
    'description': """
Agency & Freelance ERP
======================
Manage agency teams, projects, automatic team assignment, timesheets,
financials, ratings, deadline monitoring, and admin dashboard.
    """,
    'depends': [
        'project',
        'hr',
        'hr_skills',
        'hr_timesheet',
        'sale',
        'account',
        'mail',
    ],
    'data': [
        'security/agency_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/agency_track_data.xml',
        'data/ir_cron_data.xml',
        'wizard/agency_assign_wizard_views.xml',
        'views/agency_track_views.xml',
        'views/agency_team_views.xml',
        'views/agency_project_views.xml',
        'views/agency_assignment_views.xml',
        'views/agency_rating_views.xml',
        'views/agency_dashboard_views.xml',
        'views/agency_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'MIT',
}
