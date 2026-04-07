/** @odoo-module **/
/**
 * Agile Dashboard OWL Component
 *
 * Central dashboard combining:
 *  - Project selector (Scrum-enabled projects)
 *  - Active sprint summary card with progress bar
 *  - Mini BurndownChart for active sprint
 *  - VelocityChart (compact, last 6 sprints)
 *  - Team workload horizontal bars
 *  - Backlog health stat cards
 *  - Recent activity feed
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { BurndownChart } from "./burndown-chart";
import { VelocityChart } from "./velocity-chart";

class AgileDashboard extends Component {
    static template = "project_scrum.AgileDashboard";
    static props    = { action: Object };
    static components = { BurndownChart, VelocityChart };

    setup() {
        this.orm          = useService("orm");
        this.actionService = useService("action");

        this.state = useState({
            loadingProjects: true,
            loadingData:     false,
            projects:        [],
            projectId:       null,
            data:            null,   // get_dashboard_data() result
        });

        onWillStart(() => this._loadProjects());
    }

    // ── Data loading ──────────────────────────────────────────────────────────

    async _loadProjects() {
        const projects = await this.orm.searchRead(
            "project.project",
            [["enable_scrum", "=", true]],
            ["id", "name"],
            { order: "name asc", limit: 50 }
        );
        this.state.projects        = projects;
        this.state.loadingProjects = false;
        if (projects.length > 0) {
            this.state.projectId = projects[0].id;
            await this._loadDashboard(projects[0].id);
        }
    }

    async _loadDashboard(projectId) {
        this.state.loadingData = true;
        try {
            const data = await this.orm.call(
                "project.project", "get_dashboard_data", [[projectId]]
            );
            this.state.data        = data;
            this.state.loadingData = false;
        } catch (_e) {
            this.state.loadingData = false;
        }
    }

    // ── Event handlers ────────────────────────────────────────────────────────

    async onProjectChange(ev) {
        const id = parseInt(ev.target.value, 10);
        this.state.projectId = id;
        await this._loadDashboard(id);
    }

    onGoToSprintBoard() {
        this.actionService.doAction("project_scrum.action_sprint_board");
    }

    onGoToSprints() {
        this.actionService.doAction("project_scrum.action_view_all_sprints");
    }

    // ── Computed ──────────────────────────────────────────────────────────────

    get currentProject() {
        return this.state.projects.find(p => p.id === this.state.projectId) || null;
    }

    get sprint() {
        return this.state.data && this.state.data.sprint;
    }

    get teamWorkload() {
        return (this.state.data && this.state.data.team_workload) || [];
    }

    get backlogHealth() {
        return (this.state.data && this.state.data.backlog_health) || {};
    }

    get recentActivity() {
        return (this.state.data && this.state.data.recent_activity) || [];
    }
}

registry.category("actions").add("agile_dashboard_action", AgileDashboard);

export { AgileDashboard };
