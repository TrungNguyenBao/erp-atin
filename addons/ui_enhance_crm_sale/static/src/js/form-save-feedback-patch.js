/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

/**
 * Form Save Visual Feedback Patch
 * Adds brief visual pulse animations after saving CRM lead or Sale order forms.
 * Scoped by checking for module-specific CSS classes on the form element.
 */
patch(FormController.prototype, {
    async onRecordSaved(record, changes) {
        const result = await super.onRecordSaved(...arguments);
        const rootEl = this.rootRef?.el;
        if (!rootEl) {
            return result;
        }

        // CRM lead/opportunity form: flash the form sheet
        const crmForm = rootEl.querySelector(".o_lead_opportunity_form");
        if (crmForm) {
            crmForm.classList.add("ui-enhance-saved-flash");
            setTimeout(() => crmForm.classList.remove("ui-enhance-saved-flash"), 600);
            return result;
        }

        // Sale order form: pulse the totals section
        if (rootEl.querySelector(".o_sale_order")) {
            const totals = rootEl.querySelector(
                ".ui-enhance-total-section, .oe_subtotal_footer"
            );
            if (totals) {
                totals.classList.add("ui-enhance-highlight-pulse");
                setTimeout(() => totals.classList.remove("ui-enhance-highlight-pulse"), 800);
            }
        }

        return result;
    },
});
