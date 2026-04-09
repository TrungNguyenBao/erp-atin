/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class FinanceDashboard extends Component {
    static template = "project_finance_report.FinanceDashboard";

    setup() {
        this.orm = useService("orm");
        this.revenueChartRef = useRef("revenueChart");
        this.agingChartRef = useRef("agingChart");
        this.state = useState({
            totals: { revenue: 0, cost: 0, gross_profit: 0, receivable: 0, payable: 0 },
            projects: [],
        });
        this._charts = [];

        onMounted(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.fetchData();
        });

        onWillUnmount(() => this._destroyCharts());
    }

    async fetchData() {
        const data = await this.orm.call(
            "project.revenue.report", "get_dashboard_data", []
        );
        Object.assign(this.state.totals, data.totals);
        this.state.projects = data.projects;
        this._renderCharts(data);
    }

    async onRefresh() {
        this._destroyCharts();
        await this.fetchData();
    }

    formatCurrency(value) {
        return new Intl.NumberFormat("vi-VN", {
            style: "currency",
            currency: "VND",
            maximumFractionDigits: 0,
        }).format(value || 0);
    }

    _renderCharts(data) {
        this._destroyCharts();
        this._renderRevenueChart(data.projects);
        this._renderAgingChart(data.aging);
    }

    _renderRevenueChart(projects) {
        const ctx = this.revenueChartRef.el;
        if (!ctx) return;
        const chart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: projects.map((p) => p.name),
                datasets: [
                    {
                        label: "Revenue",
                        data: projects.map((p) => p.revenue),
                        backgroundColor: "rgba(40, 167, 69, 0.7)",
                    },
                    {
                        label: "Cost",
                        data: projects.map((p) => p.cost),
                        backgroundColor: "rgba(220, 53, 69, 0.7)",
                    },
                    {
                        label: "Profit",
                        data: projects.map((p) => p.profit),
                        backgroundColor: "rgba(0, 123, 255, 0.7)",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } },
            },
        });
        this._charts.push(chart);
    }

    _renderAgingChart(aging) {
        const ctx = this.agingChartRef.el;
        if (!ctx || !aging) return;
        const chart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"],
                datasets: [{
                    data: [
                        aging.current || 0,
                        aging.days_30 || 0,
                        aging.days_60 || 0,
                        aging.days_90 || 0,
                        aging.over_90 || 0,
                    ],
                    backgroundColor: [
                        "#28a745", "#ffc107", "#fd7e14", "#dc3545", "#6f42c1",
                    ],
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
        this._charts.push(chart);
    }

    _destroyCharts() {
        this._charts.forEach((c) => c.destroy());
        this._charts = [];
    }
}

registry.category("actions").add("project_finance_dashboard", FinanceDashboard);
