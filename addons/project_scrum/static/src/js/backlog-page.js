/** @odoo-module **/
/**
 * Backlog Page OWL Component
 *
 * Full-page table view for product backlog with:
 *  - Project selector
 *  - Epic grouping toggle
 *  - Inline story points editing
 *  - Reorder buttons
 *  - "Add to Sprint" action per task
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const TASK_TYPE_LABEL = {
    story: 'Story', task: 'Task', bug: 'Bug',
    improvement: 'Improvement', epic: 'Epic',
};

class BacklogPage extends Component {
    static template = "project_scrum.BacklogPage";
    static props = { action: { type: Object, optional: true }, "*": true };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");

        this.state = useState({
            loading: true,
            projects: [],
            projectId: null,
            sprints: [],
            data: null,
            groupByEpic: false,
            editingTaskId: null,
            editingSP: 0,
            searchQuery: '',
        });

        onWillStart(() => this._loadProjects());
    }

    // ── Data loading ──────────────────────────────────────────────────────────

    async _loadProjects() {
        const projects = await this.orm.searchRead(
            "project.project", [["enable_scrum", "=", true]],
            ["id", "name"], { order: "name asc", limit: 50 }
        );
        this.state.projects = projects;
        if (projects.length > 0) {
            this.state.projectId = projects[0].id;
            await this._loadBacklog(projects[0].id);
        }
        this.state.loading = false;
    }

    async _loadBacklog(projectId) {
        this.state.loading = true;
        try {
            const [data, sprints] = await Promise.all([
                this.orm.call("project.task", "get_backlog_page_data", [projectId]),
                this.orm.searchRead("project.sprint",
                    [["project_id", "=", projectId], ["state", "in", ["draft", "active", "review"]]],
                    ["id", "name", "state"], { order: "state desc, start_date desc", limit: 10 }),
            ]);
            this.state.data = data;
            this.state.sprints = sprints;
        } catch (_e) {
            this.notification.add("Failed to load backlog.", { type: "danger" });
        }
        this.state.loading = false;
    }

    // ── Computed ──────────────────────────────────────────────────────────────

    get filteredTasks() {
        if (!this.state.data) return [];
        let tasks = this.state.data.tasks;
        const q = this.state.searchQuery.toLowerCase();
        if (q) tasks = tasks.filter(t => t.name.toLowerCase().includes(q));
        return tasks;
    }

    get groupedTasks() {
        if (!this.state.groupByEpic) return null;
        const groups = {};
        for (const t of this.filteredTasks) {
            const key = t.epic_id || 0;
            if (!groups[key]) groups[key] = { epic_name: t.epic_name, tasks: [] };
            groups[key].tasks.push(t);
        }
        return Object.values(groups);
    }

    get stats() {
        return (this.state.data && this.state.data.stats) || { total: 0, unestimated: 0, total_sp: 0 };
    }

    get taskTypeLabel() { return TASK_TYPE_LABEL; }

    // ── Event handlers ────────────────────────────────────────────────────────

    async onProjectChange(ev) {
        const id = parseInt(ev.target.value, 10);
        this.state.projectId = id;
        await this._loadBacklog(id);
    }

    onSearchInput(ev) {
        this.state.searchQuery = ev.target.value;
    }

    toggleGroupByEpic() {
        this.state.groupByEpic = !this.state.groupByEpic;
    }

    // ── Inline SP edit ────────────────────────────────────────────────────────

    onEditSP(taskId, currentSP) {
        this.state.editingTaskId = taskId;
        this.state.editingSP = currentSP;
    }

    onEditSPChange(ev) {
        this.state.editingSP = parseInt(ev.target.value, 10) || 0;
    }

    async onEditSPBlur(taskId) {
        this.state.editingTaskId = null;
        const task = this.state.data.tasks.find(t => t.id === taskId);
        if (task && task.story_points !== this.state.editingSP) {
            task.story_points = this.state.editingSP;
            await this.orm.write("project.task", [taskId], { story_points: this.state.editingSP });
            // Update stats
            this.state.data.stats.total_sp = this.state.data.tasks.reduce((s, t) => s + t.story_points, 0);
            this.state.data.stats.unestimated = this.state.data.tasks.filter(t => !t.story_points).length;
        }
    }

    // ── Sprint assignment ─────────────────────────────────────────────────────

    async onAddToSprint(taskId, sprintId) {
        try {
            await this.orm.call("project.sprint", "move_task_to_sprint", [[sprintId], taskId]);
            this.state.data.tasks = this.state.data.tasks.filter(t => t.id !== taskId);
            this.state.data.stats.total--;
            this.notification.add("Task added to sprint.", { type: "success" });
        } catch (_e) {
            this.notification.add("Failed to add task to sprint.", { type: "danger" });
        }
    }

    // ── Task navigation ───────────────────────────────────────────────────────

    onTaskClick(taskId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("backlog_page_action", BacklogPage);

export { BacklogPage };
