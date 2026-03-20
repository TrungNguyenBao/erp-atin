/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

/**
 * Color picker field widget with hex input and swatch preview.
 * Registered as "tf_color_picker" for use on char fields in settings forms.
 * Falls back to native <input type="color"> + text input.
 */
class TfColorPicker extends Component {
    static template = "theme_flavor.ColorPicker";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({
            color: this.props.record.data[this.props.name] || "#714B67",
        });
    }

    onColorChange(ev) {
        this.state.color = ev.target.value;
        this.props.record.update({ [this.props.name]: ev.target.value });
    }

    onTextChange(ev) {
        const val = ev.target.value;
        if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
            this.state.color = val;
            this.props.record.update({ [this.props.name]: val });
        }
    }
}

registry.category("fields").add("tf_color_picker", {
    component: TfColorPicker,
    supportedTypes: ["char"],
});
