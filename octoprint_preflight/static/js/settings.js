/*
 * View model for OctoPrint-Preflight
 *
 * Author: Seth Battis
 * License: AGPLv3
 */

$(function () {
    function PreflightSettingsViewModel(parameters) {

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PreflightSettingsViewModel,
        elements: ['#plugin_preflight_settings']
    });
});
