#!/usr/bin/env python3
"""Load demo data for project_scrum module on Odoo 18."""
import odoo
from datetime import date, timedelta

odoo.tools.config.parse_config([
    '-c', '/etc/odoo/odoo.conf', '-d', 'odoo', '--no-http',
])

registry = odoo.registry('odoo')
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    # Check if already loaded
    if env['project.project'].search([('name', '=', 'E-Commerce Platform')]):
        print('Demo already loaded.')
        exit(0)

    today = date.today()
    admin_id = 2

    # Project
    project = env['project.project'].create({
        'name': 'E-Commerce Platform',
        'enable_scrum': True,
        'allow_milestones': True,
        'allow_task_dependencies': True,
        'user_id': admin_id,
        'privacy_visibility': 'employees',
        'color': 2,
    })

    # Stages
    stages = env['project.task.type'].search([], limit=4, order='sequence')
    project.type_ids = stages
    s_new, s_prog, s_review, s_done = stages[0], stages[1], stages[2], stages[3]

    # Epics
    epics = {}
    for name, color in [('User Authentication', 2), ('Product Catalog', 4), ('Checkout & Payment', 10)]:
        epics[name] = env['project.epic'].create({
            'name': name, 'project_id': project.id, 'color': color,
        })

    # Sprints
    sprint1 = env['project.sprint'].create({
        'name': 'Sprint 1 - Foundation', 'project_id': project.id,
        'goal': 'Set up infrastructure and core authentication',
        'start_date': today - timedelta(weeks=4), 'end_date': today - timedelta(weeks=2),
        'state': 'done', 'capacity_points': 21, 'velocity': 18,
        'review_notes': '<p>Completed core auth. OAuth deferred.</p>',
        'retro_went_well': '<p>Good collaboration. CI/CD set up early.</p>',
        'retro_went_wrong': '<p>Underestimated OAuth complexity.</p>',
        'retro_action_items': '<p>Break down stories > 8 pts.</p>',
    })
    sprint2 = env['project.sprint'].create({
        'name': 'Sprint 2 - Catalog', 'project_id': project.id,
        'goal': 'Product catalog with search and filtering',
        'start_date': today - timedelta(weeks=1), 'end_date': today + timedelta(weeks=1),
        'state': 'active', 'capacity_points': 21,
    })
    sprint3 = env['project.sprint'].create({
        'name': 'Sprint 3 - Checkout', 'project_id': project.id,
        'goal': 'Checkout flow and payment integration',
        'start_date': today + timedelta(weeks=1), 'end_date': today + timedelta(weeks=3),
        'state': 'draft', 'capacity_points': 21,
    })

    # Release
    env['project.release'].create({
        'name': 'v1.0 - MVP Launch', 'project_id': project.id,
        'target_date': today + timedelta(weeks=4), 'state': 'in_progress',
        'sprint_ids': [(6, 0, [sprint1.id, sprint2.id, sprint3.id])],
    })

    # Sprint 1 tasks (closed)
    T = env['project.task']
    ea = epics['User Authentication']
    for name, pts, state in [
        ('Set up CI/CD pipeline', 3, '1_done'),
        ('User registration with email verification', 5, '1_done'),
        ('Login with JWT tokens', 5, '1_done'),
        ('Password reset flow', 5, '1_done'),
        ('OAuth2 integration (deferred)', 13, '1_canceled'),
    ]:
        T.create({
            'name': name, 'project_id': project.id, 'sprint_id': sprint1.id,
            'epic_id': ea.id, 'story_points': pts, 'state': state,
            'stage_id': s_done.id if state == '1_done' else s_new.id,
            'user_ids': [(4, admin_id)],
        })

    # Sprint 2 tasks (active)
    ec = epics['Product Catalog']
    for name, pts, state, stage, blocked in [
        ('Product listing with pagination', 5, '1_done', s_done, False),
        ('Product search with full-text', 5, '03_approved', s_review, False),
        ('Category filtering & navigation', 5, '01_in_progress', s_prog, False),
        ('Product detail page with gallery', 3, '01_in_progress', s_prog, True),
        ('Caching strategy spike', 3, '01_in_progress', s_new, False),
    ]:
        vals = {
            'name': name, 'project_id': project.id, 'sprint_id': sprint2.id,
            'epic_id': ec.id, 'story_points': pts, 'state': state,
            'stage_id': stage.id, 'user_ids': [(4, admin_id)],
        }
        if blocked:
            vals.update({
                'is_blocked': True,
                'blocker_description': 'Waiting for image assets from design team',
                'blocker_owner_id': admin_id,
            })
        T.create(vals)

    # Backlog tasks
    eck = epics['Checkout & Payment']
    for name, pts, epic in [
        ('Shopping cart with quantity mgmt', 5, eck),
        ('Stripe payment integration', 8, eck),
        ('Order confirmation email', 3, eck),
        ('Address autocomplete', 3, eck),
        ('Refactor DB connection pooling', 2, None),
    ]:
        T.create({
            'name': name, 'project_id': project.id,
            'epic_id': epic.id if epic else False,
            'story_points': pts, 'stage_id': s_new.id,
            'priority': '1' if pts >= 5 else '0',
        })

    # Burndown daily logs
    DL = env['project.sprint.daily.log']
    s1_start = sprint1.start_date
    for offset, rem, comp, total, closed in [
        (0, 31, 0, 5, 0), (2, 28, 3, 5, 1), (4, 23, 8, 5, 2),
        (7, 18, 13, 5, 3), (11, 13, 18, 5, 4), (14, 13, 18, 5, 4),
    ]:
        DL.create({
            'sprint_id': sprint1.id, 'date': s1_start + timedelta(days=offset),
            'remaining_points': rem, 'completed_points': comp,
            'total_tasks': total, 'closed_tasks': closed,
        })

    cr.commit()
    count = T.search_count([('project_id', '=', project.id)])
    print(f'Demo loaded! Project: {project.name} | Tasks: {count} | Sprints: 3 | Epics: 3')
