/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

/**
 * Kanban Renderer UI Enhancement
 * Adds enhanced CSS class to opportunity kanban views for styling hooks.
 */
patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            const el = this.rootRef?.el;
            if (el?.closest?.(".o_opportunity_kanban")) {
                el.classList.add("ui-enhance-crm-kanban");
            }
        });
    },
});
