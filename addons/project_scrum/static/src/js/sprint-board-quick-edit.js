/** @odoo-module **/
/**
 * Sprint Board Quick Edit Modal
 *
 * Lightweight modal overlay for editing task fields without
 * navigating away from the Sprint Board.
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SprintBoardQuickEdit extends Component {
    static template = "project_scrum.SprintBoardQuickEdit";
    static props = {
        taskId: Number,
        onSave: Function,
        onClose: Function,
        onOpenFull: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            saving: false,
            name: '',
            story_points: 0,
            priority: '0',
            date_deadline: '',
            description: '',
        });
        onWillStart(() => this._loadTask());
    }

    async _loadTask() {
        try {
            const [task] = await this.orm.read("project.task", [this.props.taskId], [
                'name', 'story_points', 'priority', 'date_deadline', 'description',
            ]);
            this.state.name = task.name || '';
            this.state.story_points = task.story_points || 0;
            this.state.priority = task.priority || '0';
            this.state.date_deadline = task.date_deadline || '';
            this.state.description = task.description || '';
        } catch (_e) {
            this.notification.add("Failed to load task.", { type: "danger" });
            this.props.onClose();
        }
        this.state.loading = false;
    }

    onFieldChange(field, ev) {
        if (field === 'story_points') {
            this.state[field] = parseInt(ev.target.value, 10) || 0;
        } else {
            this.state[field] = ev.target.value;
        }
    }

    async onSave() {
        this.state.saving = true;
        try {
            await this.orm.write("project.task", [this.props.taskId], {
                name: this.state.name,
                story_points: this.state.story_points,
                priority: this.state.priority,
                date_deadline: this.state.date_deadline || false,
            });
            this.props.onSave();
        } catch (_e) {
            this.notification.add("Failed to save.", { type: "danger" });
        }
        this.state.saving = false;
    }

    onOverlayClick(ev) {
        if (ev.target === ev.currentTarget) {
            this.props.onClose();
        }
    }
}
