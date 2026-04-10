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

import { Component, useState, useRef, onWillStart, onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { BurndownChart } from "./burndown-chart";
import { VelocityChart } from "./velocity-chart";

class AgileDashboard extends Component {
    static template = "project_scrum.AgileDashboard";
    static props    = { action: { type: Object, optional: true }, "*": true };
    static components = { BurndownChart, VelocityChart };

    setup() {
        this.orm          = useService("orm");
        this.actionService = useService("action");
        this.pieChartRef   = useRef("pieChart");
        this._pieChart     = null;

        this.state = useState({
            loadingProjects: true,
            loadingData:     false,
            projects:        [],
            projectId:       null,
            data:            null,   // get_dashboard_data() result
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this._loadProjects();
        });
        onPatched(() => this._renderPieChart());
        onWillUnmount(() => this._destroyPieChart());
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

    get kpiCards() {
        const kpi = (this.state.data && this.state.data.kpi) || {};
        return [
            { key: 'projects', label: 'Scrum Projects', value: kpi.total_projects || 0, icon: 'folder' },
            { key: 'sprints', label: 'Active Sprints', value: kpi.active_sprints || 0, icon: 'refresh' },
            { key: 'rate', label: 'Completion', value: (kpi.completion_rate || 0) + '%', icon: 'check' },
            { key: 'velocity', label: 'Velocity', value: kpi.team_velocity || 0, icon: 'bolt' },
            { key: 'overdue', label: 'Overdue', value: kpi.overdue_tasks || 0, icon: 'warning' },
        ];
    }

    get taskDistribution() {
        return (this.state.data && this.state.data.task_distribution) || [];
    }

    // ── Pie chart ────────────────────────────────────────────────────────────

    _renderPieChart() {
        const ctx = this.pieChartRef.el;
        if (!ctx || this.taskDistribution.length === 0) return;
        this._destroyPieChart();
        const colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
                        '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac'];
        this._pieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.taskDistribution.map(d => d.stage),
                datasets: [{
                    data: this.taskDistribution.map(d => d.count),
                    backgroundColor: colors.slice(0, this.taskDistribution.length),
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: { position: 'bottom', labels: { fontSize: 11 } },
            },
        });
    }

    _destroyPieChart() {
        if (this._pieChart) {
            this._pieChart.destroy();
            this._pieChart = null;
        }
    }
}

registry.category("actions").add("agile_dashboard_action", AgileDashboard);

export { AgileDashboard };
