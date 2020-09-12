/*jslint esversion: 9 */
/*global $,OctoPrint,OCTOPRINT_VIEWMODELS,UI_API_KEY */

/*
 * View model for OctoPrint-Preflight
 *
 * Author: Seth Battis
 * License: AGPLv3
 */

$(function () {
    "use strict";
    const PLUGIN_ID = 'preflight';

    function PreflightViewModel() {

        const START = 'start';
        const COMPLETE = 'complete';

        const self = this;

        const DIALOG = document.querySelector('#plugin_preflight_modal');
        const API_CONFIG = {
            url: OctoPrint.getSimpleApiUrl(PLUGIN_ID),
            contentType: 'application/json'
        };
        if (UI_API_KEY) {
            API_CONFIG.headers = {'X-Api-Key': UI_API_KEY};
        }

        async function state() {
            const data = await $.ajax(API_CONFIG);
            if (data.state === 'started') {
                await showPreflightDialog();
            }
        }

        async function fireStartEvent() {
            await $.ajax({...API_CONFIG, method: 'POST', data: JSON.stringify({command: START})});
        }

        async function fireCompleteEvent() {
            await $.ajax({...API_CONFIG, method: 'POST', data: JSON.stringify({command: COMPLETE})});
        }

        function testPreflightComplete() {
            if (DIALOG.querySelectorAll('.checklist-item.unchecked').length === 0) {
                closePreflightDialog();
            }
        }

        function toggleItem(event) {
            const item = event.target.closest('.checklist-item');
            if (item.classList.contains('checked')) {
                item.classList.remove('checked');
                item.classList.add('unchecked');
            } else {
                item.classList.remove('unchecked');
                item.classList.add('checked');
            }
            testPreflightComplete();
        }

        function checklistItem(checklist, item, index, settings) {
            const elt = checklist.appendChild(document.createElement('div'));
            elt.outerHTML = `
                <div id="plugin_preflight_checklist_item_${index}" class="checklist-item unchecked">
                    <div class="checkbox unchecked">${settings['unchecked']}</div>
                    <div class="checkbox checked">${settings['checked']}</div>
                    <div class="item">${item['item']}</div>
                    ${item['directions'] && `<div class="directions">${item['directions']}</div>` || ''}
                </div>
            `;
            DIALOG.querySelector(`#plugin_preflight_checklist_item_${index}`).addEventListener('click', toggleItem);
        }

        async function showPreflightDialog() {
            const settings = await OctoPrint.settings.getPluginSettings(PLUGIN_ID);
            const checklist = DIALOG.querySelector('.checklist');
            checklist.innerHTML = "";
            let index = 0;
            for (const item of settings['checklist']) {
                checklistItem(checklist, item, ++index, settings);
            }
            DIALOG.querySelector('.modal-title').innerHTML = settings['title'];
            $(DIALOG).modal({
                backdrop: 'static',
                keyboard: false,
                show: true
            });
        }

        function closePreflightDialog() {
            $(DIALOG).modal('hide');
            fireCompleteEvent();
        }

        self.onEventPrintStarted = function () {
            showPreflightDialog();
            fireStartEvent();
        };

        state();
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PreflightViewModel,
        elements: ['#plugin_preflight_modal']
    });
});
