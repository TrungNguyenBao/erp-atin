/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState, onMounted } from "@odoo/owl";

/**
 * Patch WebClient to add vertical sidebar and icon overrides.
 * All state is read from the theme_flavor service via useService.
 */
patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this._tfThemeService = useService("theme_flavor");
        this._tfMenuService = useService("menu");
        this._tfSidebarState = useState({ collapsed: false });
    },

    get tfIsVerticalLayout() {
        return this._tfThemeService?.menuLayout === "vertical";
    },

    get tfSidebarCollapsed() {
        return this._tfSidebarState?.collapsed || false;
    },

    get tfSidebarApps() {
        return this._tfMenuService?.getApps?.() || [];
    },

    get tfCurrentApp() {
        return this._tfMenuService?.getCurrentApp?.();
    },

    tfGetAppHref(app) {
        return `/odoo/${app.actionPath || "action-" + app.actionID}`;
    },

    tfOnSidebarAppClick(app) {
        if (app) this._tfMenuService?.selectMenu?.(app);
    },

    tfOnToggleSidebar() {
        if (this._tfSidebarState) {
            this._tfSidebarState.collapsed = !this._tfSidebarState.collapsed;
        }
    },

    tfOnOpenActivities() {
        this.actionService?.doAction?.("mail.mail_activity_action");
    },

    tfOnOpenShortcuts() {
        document.dispatchEvent(new KeyboardEvent("keydown", {
            key: "?", altKey: true, bubbles: true,
        }));
    },

    tfOnOpenWorkArea() {
        window.location.href = "/odoo";
    },

    tfGetAppIconOverride(app) {
        return this._tfThemeService?.iconOverrides?.[app.id] || null;
    },
});
