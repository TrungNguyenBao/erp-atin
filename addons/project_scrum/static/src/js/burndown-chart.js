/** @odoo-module **/
/**
 * Sprint Burndown Chart OWL Component
 *
 * Renders an interactive Chart.js line chart showing:
 *  - Ideal burn line: straight decline from total SP to 0
 *  - Actual burn line: from sprint daily logs, green when on/ahead, red when behind
 * Usage: <BurndownChart sprintId="sprintId" />
 */

import { Component, onMounted, onWillUnmount, onPatched, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

class BurndownChart extends Component {
    static template = "project_scrum.BurndownChart";
    static props = {
        sprintId: { type: Number, optional: true },
        height:   { type: String, optional: true },  // e.g. "220px"
    };
    static defaultProps = {
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
            status:  "on_track",  // "on_track" | "behind" | "no_data"
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
        if (!this.props.sprintId) {
            this.state.empty   = true;
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "project.sprint", "get_burndown_data", [[this.props.sprintId]]
            );
            this.state.data    = data;
            this.state.empty   = !data.actual || data.actual.length === 0;
            this.state.loading = false;
            if (!this.state.empty) {
                this._detectStatus(data);
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

    // ── Status detection ──────────────────────────────────────────────────────

    _detectStatus(data) {
        const { actual, ideal_labels, ideal, labels } = data;
        if (!actual.length) {
            this.state.status = "no_data";
            return;
        }
        const lastActual = actual[actual.length - 1];
        // Find corresponding ideal value for the last actual date
        const lastLabel = labels[labels.length - 1];
        const idealIdx  = ideal_labels.indexOf(lastLabel);
        const lastIdeal = idealIdx >= 0 ? ideal[idealIdx] : null;

        if (lastIdeal === null) {
            this.state.status = "on_track";
        } else {
            this.state.status = lastActual <= lastIdeal ? "on_track" : "behind";
        }
    }

    // ── Chart construction ────────────────────────────────────────────────────

    _buildChart(data) {
        const canvas = this.canvasRef.el;
        if (!canvas || !window.Chart) return;

        const isBehind     = this.state.status === "behind";
        const actualColor  = isBehind ? "#DC3545" : "#28A745";
        const actualFill   = isBehind ? "rgba(220,53,69,0.08)" : "rgba(40,167,69,0.08)";

        // Merge ideal_labels + labels for unified X axis
        const allLabels = [...new Set([...data.ideal_labels, ...data.labels])].sort();

        // Map actual values to allLabels positions
        const actualMap = {};
        data.labels.forEach((lbl, i) => { actualMap[lbl] = data.actual[i]; });
        const idealMap = {};
        data.ideal_labels.forEach((lbl, i) => { idealMap[lbl] = data.ideal[i]; });

        const actualDataset = allLabels.map(l => actualMap[l] !== undefined ? actualMap[l] : null);
        const idealDataset  = allLabels.map(l => idealMap[l]  !== undefined ? idealMap[l]  : null);

        this.chart = new window.Chart(canvas, {
            type: "line",
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: "Ideal",
                        data: idealDataset,
                        borderColor: "#0D6EFD",
                        borderDash: [6, 3],
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        tension: 0,
                        spanGaps: true,
                    },
                    {
                        label: "Actual",
                        data: actualDataset,
                        borderColor: actualColor,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: actualColor,
                        backgroundColor: actualFill,
                        fill: "origin",
                        tension: 0.2,
                        spanGaps: false,
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
                                const suffix = ctx.dataset.label === "Ideal"
                                    ? ` SP (ideal)` : ` SP remaining`;
                                return `${Math.round(val)}${suffix}`;
                            },
                            afterBody: (items) => {
                                const actual = items.find(i => i.dataset.label === "Actual");
                                const ideal  = items.find(i => i.dataset.label === "Ideal");
                                if (!actual || !ideal || actual.parsed.y === null) return [];
                                const delta = actual.parsed.y - ideal.parsed.y;
                                const sign  = delta > 0 ? "+" : "";
                                const label = delta > 0 ? "behind" : "ahead";
                                return [`Δ ${sign}${Math.round(delta)} SP ${label}`];
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { font: { size: 11 }, maxRotation: 0 },
                        grid: { color: "#f1f3f5" },
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: (data.total_sp || 10) * 1.1,
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

    // ── Helpers ───────────────────────────────────────────────────────────────

    get statusBadge() {
        const map = {
            on_track: { cls: "badge-on-track", label: "✓ On Track" },
            behind:   { cls: "badge-behind",   label: "⚠ Behind" },
            no_data:  { cls: "badge-no-data",  label: "No Data" },
        };
        return map[this.state.status] || map.no_data;
    }
}

export { BurndownChart };
