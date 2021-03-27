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

const SETTINGS_CONFIG = {
    starters_npcs: {
        starters: ["Randomize Starters?", UiSwitch],
        npcs: ["Randomize NPCs and Bosses?", UiSwitch],
        global_items: ["Randomize Treasure Town shop and dungeon rewards?", UiSwitch],
        overworld_music: ["Randomize Overworld Music?", UiSwitch]
    },
    dungeons: {
        mode: ["Mode", UiSelect, {0: "Fully random floors", 1: "Keep floors in a dungeon similar"}],
        layouts: ["Randomize Layouts and Tilesets?", UiSwitch],
        weather: ["Randomize Weather?", UiSelect, {
            0: "Don't randomize",
            1: "Fully random every visit",
            2: "Random pre-generated",
            3: "Random pre-generated, lower chance of damaging weather"
        }],
        items: ["Randomize Items?", UiSwitch],
        pokemon: ["Randomize Pokémon Spawns?", UiSwitch],
        traps: ["Randomize Traps?", UiSwitch],
        fixed_rooms: ["Randomize Boss Room Layouts?", UiSwitch],
        settings: ["Dungeon Settings", UiGridTable, {
            _name: ["Dungeon", String, (id) => window.DUNGEON_NAMES[id]],
            randomize: ["Ramdomize?", UiSwitch],
            monster_houses: ["Allow Monster Houses?", UiSwitch],
            randomize_weather: ["Randomize Weather?", UiSwitch],
            enemy_iq: ["Randomize IQ?", UiSwitch],
            unlock: ["Unlock?", UiSwitch],
        }]
    },
    improvements: {
        download_portraits: ["Download missing portraits?", UiSwitch],
        patch_moveshortcuts: ["Apply \"MoveShortcuts\" patch?", UiSwitch],
        patch_unuseddungeonchance: ["Apply \"UnusedDungeonChance\" patch?", UiSwitch],
        patch_totalteamcontrol: ["Apply \"Complete Team Control\" patches?", UiSwitch],
    },
    pokemon: {
        iq_groups: ["Randomize IQ Groups?", UiSwitch],
        abilities: ["Randomize Abilities?", UiSwitch],
        typings: ["Randomize Typings?", UiSwitch],
        movesets: ["Randomize Movesets?", UiSelect, {
            0: "No",
            1: "Yes, fully random",
            2: "Yes, first move deals damage",
            3: "Yes, first move deals damage + STAB"
        }],
        ban_unowns: ["Ban Unowns?", UiSwitch],
        abilities_enabled: ["Enabled Abilities", 'abilities_enabled']
    },
    locations: {
        randomize: ["Randomize Location Names?", UiSwitch],
        first: ["First Word", UiTextField],
        second: ["Second Word", UiTextField],
    },
    chapters: {
        randomize: ["Randomize Chapter Names?", UiSwitch],
        text: ["Name List", UiTextField]
    },
    text: {
        main: ["Randomize Main Texts?", UiSwitch],
        story: ["Randomize Story Dialogue?", UiSwitch],
    }
}

function parseHelp(txt) {
    return txt ? txt : 'No help available.';
}

export default function Settings(props) {
    const rows = [];
    for (const fieldName in SETTINGS_CONFIG[props.for]) {
        const fieldConfig = SETTINGS_CONFIG[props.for][fieldName];
        let field;
        const id = props.for + '-' + fieldName;
        switch (fieldConfig[1]) {
            case UiSwitch:
                field = <UiSwitch
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    label={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                />
                break;
            case UiSelect:
                field = <UiSelect
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    options={fieldConfig[2]}
                    label={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
                />
                break;
            case UiTextField:
                field = <UiTextField
                    id={id}
                    initial={window.loadedConfig[props.for][fieldName]}
                    label={fieldConfig[0]}
                />
                break;
            case 'abilities_enabled':
                // This one is a bit special...
                let adata = {};
                for (const ability_id in window.ABILITY_NAMES) {
                    const ability_name = window.ABILITY_NAMES[ability_id];
                    adata[ability_id] = ([ability_id, window.loadedConfig[props.for][fieldName].includes(parseInt(ability_id)), ability_name]);
                }
                field = <UiGridTable
                    id={id}
                    headings={["ID", "Use?", "Ability"]}
                    switches={[1]}
                    data={adata}
                    title={fieldConfig[0]}
                    help={parseHelp(window.HELP_TEXTS[props.for][fieldName])}
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
