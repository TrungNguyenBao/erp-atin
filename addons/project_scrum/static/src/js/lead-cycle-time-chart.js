/** @odoo-module **/
/**
 * Lead/Cycle Time Chart OWL Component
 *
 * Scatter plot showing lead time and cycle time for completed tasks.
 */

import { Component, useState, useRef, onWillStart, onPatched, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

class LeadCycleTimeChart extends Component {
    static template = "project_scrum.LeadCycleTimeChart";
    static props = { action: { type: Object, optional: true }, "*": true };

    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("lctCanvas");
        this._chart = null;
        this.state = useState({
            loading: true,
            projects: [],
            projectId: null,
            data: null,
        });
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this._loadProjects();
        });
        onPatched(() => this._renderChart());
        onWillUnmount(() => { if (this._chart) this._chart.destroy(); });
    }

    async _loadProjects() {
        const projects = await this.orm.searchRead(
            "project.project", [["enable_scrum", "=", true]],
            ["id", "name"], { order: "name asc", limit: 50 }
        );
        this.state.projects = projects;
        if (projects.length) {
            this.state.projectId = projects[0].id;
            await this._loadData(projects[0].id);
        }
        this.state.loading = false;
    }

    async _loadData(projectId) {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "project.project", "get_cycle_time_data", [[projectId]]
        );
        this.state.loading = false;
    }

    async onProjectChange(ev) {
        this.state.projectId = parseInt(ev.target.value, 10);
        await this._loadData(this.state.projectId);
    }

    get averages() {
        return this.state.data?.averages || { lead: 0, cycle: 0 };
    }

    get taskCount() {
        return this.state.data?.count || 0;
    }

    _renderChart() {
        const ctx = this.chartRef.el;
        if (!ctx || !this.state.data?.tasks?.length) return;
        if (this._chart) this._chart.destroy();

        const tasks = this.state.data.tasks;
        this._chart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Lead Time (days)',
                        data: tasks.map((t, i) => ({ x: i + 1, y: t.lead_time })),
                        backgroundColor: 'rgba(78, 121, 167, 0.6)',
                        pointRadius: 5,
                    },
                    {
                        label: 'Cycle Time (days)',
                        data: tasks.map((t, i) => ({ x: i + 1, y: t.cycle_time })),
                        backgroundColor: 'rgba(242, 142, 43, 0.6)',
                        pointRadius: 5,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Task #' } },
                    y: { title: { display: true, text: 'Days' }, beginAtZero: true },
                },
                plugins: { legend: { position: 'bottom' } },
            },
        });
    }
}

registry.category("actions").add("lead_cycle_time_action", LeadCycleTimeChart);
export { LeadCycleTimeChart };
