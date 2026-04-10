/** @odoo-module **/
/**
 * Cumulative Flow Diagram OWL Component
 *
 * Stacked area chart showing task distribution across stages over time.
 */

import { Component, useState, useRef, onWillStart, onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

const COLORS = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
                '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac'];

class CfdChart extends Component {
    static template = "project_scrum.CfdChart";
    static props = { action: Object };

    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("cfdCanvas");
        this._chart = null;
        this.state = useState({
            loading: true,
            sprints: [],
            sprintId: null,
            data: null,
        });
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this._loadSprints();
        });
        onPatched(() => this._renderChart());
        onWillUnmount(() => { if (this._chart) this._chart.destroy(); });
    }

    async _loadSprints() {
        const sprints = await this.orm.searchRead(
            "project.sprint",
            [["state", "in", ["active", "review", "done"]]],
            ["id", "name", "state"],
            { order: "state asc, start_date desc", limit: 20 }
        );
        this.state.sprints = sprints;
        if (sprints.length) {
            this.state.sprintId = sprints[0].id;
            await this._loadData(sprints[0].id);
        }
        this.state.loading = false;
    }

    async _loadData(sprintId) {
        this.state.loading = true;
        this.state.data = await this.orm.call("project.sprint", "get_cfd_data", [[sprintId]]);
        this.state.loading = false;
    }

    async onSprintChange(ev) {
        this.state.sprintId = parseInt(ev.target.value, 10);
        await this._loadData(this.state.sprintId);
    }

    _renderChart() {
        const ctx = this.chartRef.el;
        if (!ctx || !this.state.data?.datasets?.length) return;
        if (this._chart) this._chart.destroy();

        const { labels, datasets } = this.state.data;
        this._chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: datasets.map((ds, i) => ({
                    label: ds.stage,
                    data: ds.data,
                    backgroundColor: COLORS[i % COLORS.length] + '40',
                    borderColor: COLORS[i % COLORS.length],
                    borderWidth: 1.5,
                    fill: true,
                    pointRadius: 0,
                })),
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: true },
                    y: { stacked: true, beginAtZero: true },
                },
                plugins: { legend: { position: 'bottom' } },
            },
        });
    }
}

registry.category("actions").add("cfd_chart_action", CfdChart);
export { CfdChart };
