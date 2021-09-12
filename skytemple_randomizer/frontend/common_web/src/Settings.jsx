/*
 * Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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


import Grid from "@material-ui/core/Grid";
import React from "react";
import {UiTextField} from "./UiTextField";
import {UiSwitch} from "./UiSwitch";
import {UiGridTable} from "./UiGridTable";
import {UiSelect} from "./UiSelect";
import {
    ID_PREFIX,
    SETTINGS_CONFIG,
    updateListEnabledInConfig,
    updateGenericGridInConfig,
    updateInConfig
} from "./config";
import {UiSlider} from "./UiSlider";

function parseHelp(txt) {
    return txt ? txt : 'No help available.';
}

export default function Settings(props) {
    const rows = [];
    for (const fieldName in SETTINGS_CONFIG[props.for]) {
        const fieldConfig = SETTINGS_CONFIG[props.for][fieldName];
        let field;
        const id = ID_PREFIX + props.for + '-' + fieldName;
        switch (fieldConfig[1]) {
            case UiSwitch:
                field = <UiSwitch
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    label={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                    onChange={updateInConfig}
                />
                break;
            case UiSelect:
                field = <UiSelect
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    options={fieldConfig[2]}
                    label={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                    onChange={updateInConfig}
                />
                break;
            case UiTextField:
                field = <UiTextField
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    label={fieldConfig[0]}
                    onChange={updateInConfig}
                />
                break;
            case UiSlider:
                field = <UiSlider
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    label={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                    max={fieldConfig[2]}
                    onChange={updateInConfig}
                />
                break;
            case 'abilities_enabled':
            case 'items_enabled':
            case 'moves_enabled':
            case 'monsters_enabled':
                // These ones are a bit special...
                let heading;
                let adata = {};
                let updateFn;
                switch (fieldConfig[1]) {
                    case 'abilities_enabled':
                        heading = ["Ability", "Use?"];
                        for (const ability_id in window.ABILITY_NAMES) {
                            const ability_name = window.ABILITY_NAMES[ability_id];
                            adata[ability_id] = ([ability_id.toString() + ': ' + ability_name, window.loadedConfig[props.for][fieldName].includes(parseInt(ability_id))]);
                        }
                        break;
                    case 'items_enabled':
                        heading = ["Item", "Use?"];
                        for (const item_id in window.ITEM_NAMES) {
                            const item_name = window.ITEM_NAMES[item_id];
                            adata[item_id] = ([item_id.toString() + ': ' + item_name, window.loadedConfig[props.for][fieldName].includes(parseInt(item_id))]);
                        }
                        break;
                    case 'moves_enabled':
                        heading = ["Move", "Use?"];
                        for (const move_id in window.MOVE_NAMES) {
                            const move_name = window.MOVE_NAMES[move_id];
                            adata[move_id] = ([move_id.toString() + ': ' + move_name, window.loadedConfig[props.for][fieldName].includes(parseInt(move_id))]);
                        }
                        break;
                    case 'monsters_enabled':
                        heading = ["Pokémon", "Use?"];
                        for (const monster_id in window.MONSTER_NAMES) {
                            const monster_name = window.MONSTER_NAMES[monster_id];
                            adata[monster_id] = ([monster_id.toString() + ': ' + monster_name, window.loadedConfig[props.for][fieldName].includes(parseInt(monster_id))]);
                        }
                        break;
                }
                field = <UiGridTable
                    id={id}
                    headings={heading}
                    switches={[1]}
                    data={adata}
                    title={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                    onChange={updateListEnabledInConfig}
                />
                break;
            case UiGridTable:
                let headings = [];
                let switches = [];
                let data = {};
                let rowKeyIdx = 0;
                for (const rowKeyName in fieldConfig[2]) {
                    const rowConfig = fieldConfig[2][rowKeyName];
                    headings.push(rowConfig[0]);
                    // noinspection FallThroughInSwitchStatementJS
                    switch (rowConfig[1]) {
                        case UiSwitch:
                            switches.push(rowKeyIdx);
                        case String:
                            break;
                        default:
                            throw Error("Invalid cell type.");
                    }
                    rowKeyIdx++;
                }
                const flatRowData = [];
                for (const rowKey in window.loadedConfig[props.for][fieldName]) {
                    const v = window.loadedConfig[props.for][fieldName][rowKey];
                    if (typeof v != 'object') {
                        flatRowData.push({_VALUE: v, _KEY: rowKey})
                    } else {
                        flatRowData.push({...v, _KEY: rowKey})
                    }
                }
                for (const row of flatRowData) {
                    data[row['_KEY']] = [];
                    for (const rowKeyName in fieldConfig[2]) {
                        const rowConfig = fieldConfig[2][rowKeyName];
                        data[row['_KEY']].push(rowConfig.length > 2 ? rowConfig[2] : row[rowKeyName]);
                    }
                }
                field = <UiGridTable
                    id={id}
                    headings={headings}
                    switches={switches}
                    data={data}
                    title={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                    onChange={updateGenericGridInConfig}
                />
                break;
            default:
                throw Error("Unknown field.");
        }
        rows.push(<Grid item xs={12}>{field}</Grid>)
    }
    return (
        <Grid container spacing={1}>
            {rows}
        </Grid>
    )
}
