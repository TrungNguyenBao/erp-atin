/** @odoo-module **/
/**
 * Sprint Board OWL Component
 *
 * Interactive kanban board for the active sprint. Features:
 *  - Columns per project stage with task cards
 *  - Drag-and-drop between columns via useSortable
 *  - Sprint selector dropdown
 *  - Collapsible backlog sidebar for quick task assignment
 *  - Story points totals, task counts, blocked indicators
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { SprintBoardQuickEdit } from "./sprint-board-quick-edit";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// ── Task type icons (Bootstrap-style unicode shorthand) ───────────────────────
const TASK_TYPE_ICON = {
    story:       "📖",
    task:        "✅",
    bug:         "🐛",
    improvement: "⚡",
    epic:        "🚀",
};

// ── Main Sprint Board component ───────────────────────────────────────────────
class SprintBoard extends Component {
    static template = "project_scrum.SprintBoard";
    static props = { action: Object };
    static components = { SprintBoardQuickEdit };

    setup() {
        this.orm         = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            loading:       true,
            sprints:       [],       // [{id, name, state, committed_points, completed_points}]
            sprintId:      null,
            columns:       [],       // [{stage_id, stage_name, is_closed, tasks, task_count, total_sp}]
            backlogTasks:  [],       // [{id, name, story_points, ...}]
            showBacklog:   true,
            dragging:      null,     // {taskId, fromStageId}
            showQuickCreate: false,
            quickCreateName: '',
            quickCreateSP: 0,
            modalTaskId: null,
        });

        onWillStart(() => this._loadSprints());
    }

    // ── Data loading ──────────────────────────────────────────────────────────

    async _loadSprints() {
        const sprints = await this.orm.searchRead(
            "project.sprint",
            [["state", "in", ["active", "draft"]]],
            ["id", "name", "state", "committed_points", "completed_points",
             "remaining_points", "completion_percentage", "start_date", "end_date"],
            { order: "state desc, start_date desc", limit: 20 }
        );
        this.state.sprints = sprints;

        // Auto-select active sprint; fall back to first draft
        const active = sprints.find(s => s.state === "active");
        const first  = sprints[0];
        const target = active || first;
        if (target) {
            this.state.sprintId = target.id;
            await this._loadBoardData(target.id);
        } else {
            this.state.loading = false;
        }
    }

    async _loadBoardData(sprintId) {
        this.state.loading = true;
        try {
            const [boardData, backlogTasks] = await Promise.all([
                this.orm.call("project.sprint", "get_board_data", [[sprintId]]),
                this.orm.call("project.sprint", "get_backlog_tasks", [[sprintId]]),
            ]);
            this.state.columns      = boardData.columns || boardData;
            this.state.backlogTasks = backlogTasks;
            this.state.wipLimit     = boardData.wip_limit || 0;
            this.state.scrumMaster  = boardData.scrum_master || '';
        } catch (e) {
            this.notification.add("Failed to load board data.", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    // ── Computed helpers ──────────────────────────────────────────────────────

    get activeSprint() {
        return this.state.sprints.find(s => s.id === this.state.sprintId) || null;
    }

    get taskTypeIcon() {
        return TASK_TYPE_ICON;
    }

    // ── Event handlers ────────────────────────────────────────────────────────

    async onSprintChange(ev) {
        const id = parseInt(ev.target.value, 10);
        this.state.sprintId = id;
        await this._loadBoardData(id);
    }

    toggleBacklog() {
        this.state.showBacklog = !this.state.showBacklog;
    }

    // ── Drag-drop handlers ────────────────────────────────────────────────────

    onDragStart(ev, taskId, fromStageId) {
        this.state.dragging = { taskId, fromStageId };
        ev.dataTransfer.effectAllowed = "move";
        ev.dataTransfer.setData("text/plain", String(taskId));
        ev.currentTarget.classList.add("o-sprint-board__card--dragging");
    }

    onDragEnd(ev) {
        this.state.dragging = null;
        ev.currentTarget.classList.remove("o-sprint-board__card--dragging");
    }

    onDragOver(ev) {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = "move";
        ev.currentTarget.classList.add("o-sprint-board__column-body--over");
    }

    onDragLeave(ev) {
        ev.currentTarget.classList.remove("o-sprint-board__column-body--over");
    }

    async onDrop(ev, toStageId) {
        ev.preventDefault();
        ev.currentTarget.classList.remove("o-sprint-board__column-body--over");

        const taskId = parseInt(ev.dataTransfer.getData("text/plain"), 10);
        const { fromStageId } = this.state.dragging || {};

        if (!taskId || toStageId === fromStageId) return;

        // Optimistic UI update
        this._moveTaskInState(taskId, fromStageId, toStageId);
        this.state.dragging = null;

        try {
            await this.orm.write("project.task", [taskId], { stage_id: toStageId });
        } catch (e) {
            // Revert on failure
            this._moveTaskInState(taskId, toStageId, fromStageId);
            this.notification.add("Failed to move task. Please try again.", { type: "danger" });
        }
    }

    // ── Backlog assignment ────────────────────────────────────────────────────

    async onAddToSprint(taskId) {
        if (!this.state.sprintId) return;
        try {
            await this.orm.call(
                "project.sprint", "move_task_to_sprint",
                [[this.state.sprintId], taskId]
            );
            await this._loadBoardData(this.state.sprintId);
        } catch (e) {
            this.notification.add("Failed to add task to sprint.", { type: "danger" });
        }
    }

    // ── Task quick edit modal ────────────────────────────────────────────────

    onTaskClick(ev, taskId) {
        if (ev.defaultPrevented || this.state.dragging) return;
        this.state.modalTaskId = taskId;
    }

    async onModalSave() {
        this.state.modalTaskId = null;
        await this._loadBoardData(this.state.sprintId);
    }

    onModalClose() {
        this.state.modalTaskId = null;
    }

    onOpenFullForm() {
        const taskId = this.state.modalTaskId;
        this.state.modalTaskId = null;
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    // ── Backlog quick create ─────────────────────────────────────────────

    toggleQuickCreate() {
        this.state.showQuickCreate = !this.state.showQuickCreate;
        this.state.quickCreateName = '';
        this.state.quickCreateSP = 0;
    }

    onQuickCreateNameChange(ev) {
        this.state.quickCreateName = ev.target.value;
    }

    onQuickCreateSPChange(ev) {
        this.state.quickCreateSP = parseInt(ev.target.value, 10) || 0;
    }

    async onQuickCreateSubmit() {
        const name = this.state.quickCreateName.trim();
        if (!name || !this.state.sprintId) return;
        try {
            const task = await this.orm.call(
                "project.sprint", "quick_create_backlog_task",
                [[this.state.sprintId], { name, story_points: this.state.quickCreateSP }]
            );
            this.state.backlogTasks.push(task);
            this.state.quickCreateName = '';
            this.state.quickCreateSP = 0;
            this.state.showQuickCreate = false;
        } catch (e) {
            this.notification.add("Failed to create task.", { type: "danger" });
        }
    }

    // ── Backlog reorder ───────────────────────────────────────────────────

    async onBacklogReorder(taskId, direction) {
        const tasks = this.state.backlogTasks;
        const idx = tasks.findIndex(t => t.id === taskId);
        if (idx === -1) return;
        const swapIdx = direction === 'up' ? idx - 1 : idx + 1;
        if (swapIdx < 0 || swapIdx >= tasks.length) return;

        // Swap in UI
        [tasks[idx], tasks[swapIdx]] = [tasks[swapIdx], tasks[idx]];

        // Persist new sequences
        const newSeq = (swapIdx + 1) * 10;
        try {
            await this.orm.call(
                "project.sprint", "reorder_backlog_task",
                [[this.state.sprintId], taskId, newSeq]
            );
        } catch (e) {
            // Revert swap on failure
            [tasks[idx], tasks[swapIdx]] = [tasks[swapIdx], tasks[idx]];
        }
    }

    // ── Internal helpers ──────────────────────────────────────────────────────

    _moveTaskInState(taskId, fromStageId, toStageId) {
        const fromCol = this.state.columns.find(c => c.stage_id === fromStageId);
        const toCol   = this.state.columns.find(c => c.stage_id === toStageId);
        if (!fromCol || !toCol) return;

        const idx  = fromCol.tasks.findIndex(t => t.id === taskId);
        if (idx === -1) return;

        const [task] = fromCol.tasks.splice(idx, 1);
        toCol.tasks.push(task);

        // Update SP totals
        fromCol.task_count = fromCol.tasks.length;
        fromCol.total_sp   = fromCol.tasks.reduce((s, t) => s + t.story_points, 0);
        toCol.task_count   = toCol.tasks.length;
        toCol.total_sp     = toCol.tasks.reduce((s, t) => s + t.story_points, 0);
    }
}

// Register as Odoo client action
registry.category("actions").add("sprint_board_action", SprintBoard);

export { SprintBoard };
