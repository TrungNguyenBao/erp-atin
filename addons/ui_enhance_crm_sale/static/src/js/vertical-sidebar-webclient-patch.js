/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

/**
 * Patch WebClient to expose sidebar state, app data, and toolbar actions.
 * Used by vertical-sidebar-template.xml to render the sidebar.
 */
patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.sidebarMenuService = useService("menu");
        this.sidebarHotkeyService = useService("hotkey");
        this.sidebarState = useState({ collapsed: false });
    },

    /** Whether sidebar is collapsed (icon-only mode). */
    get sidebarCollapsed() {
        return this.sidebarState.collapsed;
    },

    /** All installed apps for sidebar rendering. */
    get sidebarApps() {
        return this.sidebarMenuService.getApps() || [];
    },

    /** Current active app for highlighting. */
    get currentApp() {
        return this.sidebarMenuService.getCurrentApp();
    },

    /** Generate href for an app menu item. */
    getAppHref(app) {
        return `/odoo/${app.actionPath || "action-" + app.actionID}`;
    },

    /** Navigate to selected app. */
    onSidebarAppClick(app) {
        if (app) {
            this.sidebarMenuService.selectMenu(app);
        }
    },

    /** Toggle sidebar collapsed/expanded. */
    onToggleSidebar() {
        this.sidebarState.collapsed = !this.sidebarState.collapsed;
    },

    /** Open Activity Center. */
    onOpenActivities() {
        this.actionService.doAction("mail.mail_activity_action");
    },

    /** Open Keyboard Shortcuts overlay via hotkey service. */
    onOpenShortcuts() {
        // Dispatch Alt+? to trigger Odoo's built-in shortcut overlay
        const event = new KeyboardEvent("keydown", {
            key: "?",
            altKey: true,
            bubbles: true,
        });
        document.dispatchEvent(event);
    },

    /** Open Home / Work Area (all apps view). */
    onOpenWorkArea() {
        window.location.href = "/odoo";
    },
});
