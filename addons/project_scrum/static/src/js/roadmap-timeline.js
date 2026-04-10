/** @odoo-module **/
/**
 * Roadmap Timeline OWL Component
 *
 * CSS grid Gantt-style view showing epics as horizontal bars
 * across a weekly/monthly timeline with sprint boundary markers.
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const MS_PER_DAY = 86400000;

class RoadmapTimeline extends Component {
    static template = "project_scrum.RoadmapTimeline";
    static props = { action: { type: Object, optional: true }, "*": true };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            projects: [],
            projectId: null,
            data: null,
            zoom: 'week',
        });
        onWillStart(() => this._loadProjects());
    }

    async _loadProjects() {
        const projects = await this.orm.searchRead(
            "project.project", [["enable_scrum", "=", true]],
            ["id", "name"], { order: "name asc", limit: 50 }
        );
        this.state.projects = projects;
        if (projects.length > 0) {
            this.state.projectId = projects[0].id;
            await this._loadRoadmap(projects[0].id);
        }
        this.state.loading = false;
    }

    async _loadRoadmap(projectId) {
        this.state.loading = true;
        const data = await this.orm.call("project.epic", "get_roadmap_data", [projectId]);
        this.state.data = data;
        this.state.loading = false;
    }

    async onProjectChange(ev) {
        this.state.projectId = parseInt(ev.target.value, 10);
        await this._loadRoadmap(this.state.projectId);
    }

    toggleZoom() {
        this.state.zoom = this.state.zoom === 'week' ? 'month' : 'week';
    }

    // ── Timeline computation ──────────────────────────────────────────────────

    get hasTimeline() {
        const dr = this.state.data?.date_range;
        return dr && dr.start && dr.end;
    }

    get timelineStart() {
        return new Date(this.state.data.date_range.start);
    }

    get timelineEnd() {
        // Add 2-week buffer
        const end = new Date(this.state.data.date_range.end);
        end.setDate(end.getDate() + 14);
        return end;
    }

    get totalDays() {
        return Math.ceil((this.timelineEnd - this.timelineStart) / MS_PER_DAY);
    }

    get columnHeaders() {
        const headers = [];
        const start = this.timelineStart;
        const days = this.totalDays;
        const step = this.state.zoom === 'week' ? 7 : 30;
        for (let d = 0; d < days; d += step) {
            const date = new Date(start.getTime() + d * MS_PER_DAY);
            const label = this.state.zoom === 'week'
                ? `${date.getMonth() + 1}/${date.getDate()}`
                : `${date.toLocaleString('default', { month: 'short' })}`;
            headers.push({ label, col: Math.floor(d / step) + 2 });
        }
        return headers;
    }

    get gridColCount() {
        const step = this.state.zoom === 'week' ? 7 : 30;
        return Math.ceil(this.totalDays / step);
    }

    get epicBars() {
        if (!this.hasTimeline) return [];
        const start = this.timelineStart;
        const step = this.state.zoom === 'week' ? 7 : 30;
        const colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
                        '#edc948', '#b07aa1', '#ff9da7'];

        return (this.state.data?.epics || []).filter(e => e.start_date && e.end_date).map((epic, i) => {
            const eStart = new Date(epic.start_date);
            const eEnd = new Date(epic.end_date);
            const colStart = Math.max(Math.floor((eStart - start) / MS_PER_DAY / step), 0) + 2;
            const colEnd = Math.floor((eEnd - start) / MS_PER_DAY / step) + 3;
            return {
                ...epic,
                colStart,
                colEnd: Math.max(colEnd, colStart + 1),
                color: colors[i % colors.length],
                row: i + 2,
            };
        });
    }

    get unscheduledEpics() {
        return (this.state.data?.epics || []).filter(e => !e.start_date || !e.end_date);
    }

    get sprintMarkers() {
        if (!this.hasTimeline) return [];
        const start = this.timelineStart;
        const step = this.state.zoom === 'week' ? 7 : 30;
        return (this.state.data?.sprints || []).map(s => ({
            ...s,
            col: Math.floor((new Date(s.start_date) - start) / MS_PER_DAY / step) + 2,
        }));
    }
}

registry.category("actions").add("roadmap_timeline_action", RoadmapTimeline);
export { RoadmapTimeline };
