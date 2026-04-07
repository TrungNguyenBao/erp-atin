/** @odoo-module **/
/**
 * Register BurndownChart and VelocityChart as reusable OWL components
 * accessible via the Odoo component registry.
 */

import { registry } from "@web/core/registry";
import { BurndownChart } from "./burndown-chart";
import { VelocityChart } from "./velocity-chart";

registry.category("components").add("BurndownChart", BurndownChart);
registry.category("components").add("VelocityChart", VelocityChart);
