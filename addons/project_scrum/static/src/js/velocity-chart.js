/** @odoo-module **/
/**
 * Sprint Velocity Chart OWL Component
 *
 * Renders a Chart.js grouped bar chart showing per-sprint committed vs completed SP,
 * with a rolling 3-sprint average overlay line.
 * Usage: <VelocityChart projectId="projectId" />
 */

import { Component, onMounted, onWillUnmount, onPatched, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

class VelocityChart extends Component {
    static template = "project_scrum.VelocityChart";
    static props = {
        projectId: { type: Number, optional: true },
        limit:     { type: Number, optional: true },
        height:    { type: String, optional: true },
    };
    static defaultProps = {
        limit:  6,
        height: "240px",
    };

    setup() {
        this.orm       = useService("orm");
        this.canvasRef = useRef("canvas");
        this.chart     = null;

        this.state = useState({
            loading: true,
            empty:   false,
            data:    null,
        });

        onMounted(() => this._init());
        onPatched(() => this._updateChart());
        onWillUnmount(() => this._destroyChart());
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    async _init() {
        await loadJS("/web/static/lib/Chart/Chart.js");
        await this._fetchAndRender();
    }

    async _fetchAndRender() {
        if (!this.props.projectId) {
            this.state.empty   = true;
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "project.project", "get_velocity_data",
                [[this.props.projectId], this.props.limit]
            );
            this.state.data    = data;
            this.state.empty   = !data.labels || data.labels.length === 0;
            this.state.loading = false;
            if (!this.state.empty) {
                this._destroyChart();
                this._buildChart(data);
            }
        } catch (_e) {
            this.state.loading = false;
            this.state.empty   = true;
        }
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    _updateChart() {
        if (this.state.data && !this.state.loading && !this.state.empty) {
            this._destroyChart();
            this._buildChart(this.state.data);
        }
    }

    // ── Chart construction ────────────────────────────────────────────────────

    _buildChart(data) {
        const canvas = this.canvasRef.el;
        if (!canvas || !window.Chart) return;

        this.chart = new window.Chart(canvas, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: "Committed SP",
                        data: data.committed,
                        backgroundColor: "rgba(147,197,253,0.7)",   // light blue
                        borderColor: "#93C5FD",
                        borderWidth: 1,
                        order: 2,
                    },
                    {
                        label: "Completed SP",
                        data: data.completed,
                        backgroundColor: "rgba(29,78,216,0.85)",    // dark blue
                        borderColor: "#1D4ED8",
                        borderWidth: 1,
                        order: 2,
                    },
                    {
                        label: "3-Sprint Avg",
                        data: data.rolling_avg,
                        type: "line",
                        borderColor: "#F97316",
                        borderWidth: 2.5,
                        pointRadius: 5,
                        pointBackgroundColor: "#F97316",
                        pointBorderColor: "#fff",
                        pointBorderWidth: 2,
                        fill: false,
                        tension: 0.2,
                        spanGaps: false,
                        order: 1,
                        yAxisID: "y",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 20, font: { size: 11 } },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const val = ctx.parsed.y;
                                if (val === null) return null;
                                return `${ctx.dataset.label}: ${val} SP`;
                            },
                            afterBody: (items) => {
                                const committed = items.find(i => i.dataset.label === "Committed SP");
                                const completed = items.find(i => i.dataset.label === "Completed SP");
                                if (!committed || !completed) return [];
                                const diff = committed.parsed.y - completed.parsed.y;
                                if (diff === 0) return ["✓ All points completed"];
                                return [`${diff} SP not completed`];
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { font: { size: 11 } },
                        grid: { color: "#f1f3f5" },
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { font: { size: 11 } },
                        grid: { color: "#f1f3f5" },
                        title: {
                            display: true,
                            text: "Story Points",
                            font: { size: 11 },
                            color: "#6c757d",
                        },
                    },
                },
            },
        });
    }
}

export { VelocityChart };
