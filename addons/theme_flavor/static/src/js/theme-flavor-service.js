/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { reactive } from "@odoo/owl";

/**
 * Theme Flavor Service
 * Loads theme settings from backend, applies CSS custom properties and
 * data attributes to DOM, listens for bus notifications on settings change.
 */
const themeFlavorService = {
    dependencies: ["bus_service"],

    start(env, { bus_service }) {
        const state = reactive({
            themeStyle: "flat",
            menuLayout: "horizontal",
            colors: {},
            iconOverrides: {},
            loaded: false,
        });

        /**
         * Apply theme state to DOM: set body data attributes and CSS custom properties.
         */
        function applyToDOM(s) {
            // Set data attributes for CSS selectors
            document.body.dataset.tfTheme = s.themeStyle || "flat";
            document.body.dataset.tfLayout = s.menuLayout || "horizontal";

            // Apply color custom properties to :root
            const root = document.documentElement;
            const colorMap = {
                "--tf-brand": s.colors.brand,
                "--tf-nav-bg": s.colors.nav,
                "--tf-accent": s.colors.accent,
                "--tf-btn-primary": s.colors.btnPrimary,
                "--tf-btn-secondary": s.colors.btnSecondary,
                "--tf-btn-success": s.colors.btnSuccess,
                "--tf-btn-danger": s.colors.btnDanger,
            };

            for (const [prop, val] of Object.entries(colorMap)) {
                if (val) {
                    root.style.setProperty(prop, val);
                }
            }

            // Derived colors using color-mix
            if (s.colors.brand) {
                root.style.setProperty(
                    "--tf-brand-hover",
                    `color-mix(in srgb, ${s.colors.brand} 85%, black)`
                );
                root.style.setProperty(
                    "--tf-brand-light",
                    `color-mix(in srgb, ${s.colors.brand} 15%, white)`
                );
                root.style.setProperty(
                    "--tf-brand-lighter",
                    `color-mix(in srgb, ${s.colors.brand} 8%, white)`
                );
            }

            if (s.colors.nav) {
                root.style.setProperty(
                    "--tf-nav-hover",
                    `color-mix(in srgb, ${s.colors.nav} 85%, black)`
                );
            }
        }

        /**
         * Load settings from backend via RPC.
         */
        async function loadSettings() {
            try {
                const result = await rpc("/theme_flavor/settings");
                state.themeStyle = result.themeStyle || "flat";
                state.menuLayout = result.menuLayout || "horizontal";
                state.colors = result.colors || {};
                state.loaded = true;
                applyToDOM(state);
            } catch (e) {
                // Fallback to defaults on error
                console.warn("Theme Flavor: failed to load settings, using defaults", e);
                state.loaded = true;
                applyToDOM(state);
            }
        }

        /**
         * Load icon overrides from backend.
         */
        async function loadIconOverrides() {
            try {
                const result = await rpc("/theme_flavor/icon_overrides");
                state.iconOverrides = result || {};
            } catch (e) {
                console.warn("Theme Flavor: failed to load icon overrides", e);
            }
        }

        // Listen for setting changes via bus
        bus_service.subscribe("theme_flavor/settings_changed", () => {
            loadSettings();
            loadIconOverrides();
        });

        // Load on startup
        loadSettings();
        loadIconOverrides();

        return state;
    },
};

registry.category("services").add("theme_flavor", themeFlavorService);
