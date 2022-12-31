/*
 * Copyright 2020-2023 Capypara and the SkyTemple Contributors
 *
 * This file is part of SkyTemple.
 *
 * SkyTemple is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * SkyTemple is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
 */

/** Server-based randomization implementation */

/**
 * Starts the randomization process and runs it.
 * @param {File} file
 * @param {processCallback} processCallback
 * @param {object} config - See config python module: RandomizerConfig
 */
window.startRandomization = function(file, processCallback, config) {
    fetch('/upload', {
      method: 'POST',
      body: file
    }).then( r => {
        if (!r.ok) {
            processCallback(RandomizationEventType.ERROR, {message: "Erorr during upload: " + r.status + " " + r.statusText + "."}, "???");
            return;
        }
        var host = window.location.host;
        var proto = location.protocol === 'https:' ? 'wss' : 'ws';

        var ws = new WebSocket(proto + '://' + host + '/__ws');

        ws.onopen = function () {
            // Start
            ws.send(JSON.stringify({
                action: 'start',
                config: config
            }));
        };

        var stepsBefore = 0;
        var totalStepsBefore = 1;

        ws.onmessage = function (ev) {
            var message = JSON.parse(ev.data);
            if (message.status === "progress") {
                stepsBefore = message.step;
                totalStepsBefore = message.totalSteps;
                processCallback(RandomizationEventType.PROGRESS, {
                    step: stepsBefore,
                    totalSteps: totalStepsBefore,
                    message: message.message,
                    seed: message.seed
                });
            } else if (message.status === "done") {
                processCallback(RandomizationEventType.DONE, {
                    step: stepsBefore,
                    totalSteps: totalStepsBefore,
                    message: null,
                    seed: message.seed
                });
            } else if (message.status === "error") {
                processCallback(RandomizationEventType.ERROR, {
                    step: stepsBefore,
                    totalSteps: totalStepsBefore,
                    message: message.message,
                    seed: message.seed
                });
            }
        };
    }).catch(err => {
        processCallback(RandomizationEventType.ERROR, {message: "Unexpected client error: " + err.toString()}, "???");
    });
}
