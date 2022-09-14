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

import {UiSwitch} from "./UiSwitch";
import {UiSelect} from "./UiSelect";
import {UiGridTable} from "./UiGridTable";
import {UiTextField} from "./UiTextField";
import {default as set} from 'set-value';
import {default as get} from 'get-value';
import {UiSlider} from "./UiSlider";

export const SETTINGS_CONFIG = {
    starters_npcs: {
        starters: ["Randomize Starters?", UiSwitch],
        npcs: ["Randomize NPCs and Bosses?", UiSwitch],
        topmenu_music: ["Randomize Titlescreen Music?", UiSwitch],
        overworld_music: ["Randomize Overworld Music?", UiSwitch],
        explorer_rank_unlocks: ["Randomize Explorer Rank Unlocks?", UiSwitch],
        explorer_rank_rewards: ["Randomize Explorer Rank Rewards?", UiSwitch],
        native_file_handlers: ["Use Native File Handlers", UiSwitch],
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
        min_floor_change_percent: ["Randomize Floor count (down; %)", UiSlider, 10],
        max_floor_change_percent: ["Randomize Floor count (up; %)", UiSlider, 10],
        fixed_rooms: ["Randomize Boss Room Layouts?", UiSwitch],
        max_sticky_chance: ["Max sticky item chance", UiSlider, 100],
        max_mh_chance: ["Max monster house chance", UiSlider, 100],
        max_hs_chance: ["Max hidden stairs chance", UiSlider, 100],
        max_ks_chance: ["Max Kecleon shop chance", UiSlider, 100],
        settings: ["Dungeon Settings", UiGridTable, {
            _name: ["Dungeon", String, (id) => id.toString() + ': ' + window.DUNGEON_NAMES[id]],
            randomize: ["Randomize?", UiSwitch],
            monster_houses: ["Allow Monster Houses?", UiSwitch],
            randomize_weather: ["Randomize Weather?", UiSwitch],
            enemy_iq: ["Randomize IQ?", UiSwitch],
            unlock: ["Unlock?", UiSwitch],
        }],
        items_enabled: ["Enabled Items", 'items_enabled']
    },
    improvements: {
        download_portraits: ["Download missing portraits & sprites?", UiSwitch],
        patch_moveshortcuts: ["Apply \"MoveShortcuts\" patch?", UiSwitch],
        patch_unuseddungeonchance: ["Apply \"UnusedDungeonChance\" patch?", UiSwitch],
        patch_totalteamcontrol: ["Apply \"Complete Team Control\" patches?", UiSwitch],
        patch_fixmemorysoftlock: ["Apply \"Fix Memory Softlock\" patch?", UiSwitch],
        patch_disarm_monster_houses: ["Apply \"Disarm Monster Houses\" patches?", UiSwitch],
    },
    pokemon: {
        iq_groups: ["Randomize IQ Groups?", UiSwitch],
        abilities: ["Randomize Abilities?", UiSwitch],
        typings: ["Randomize Typings?", UiSwitch],
        movesets: ["Randomize Level-Up Movesets?", UiSelect, {
            0: "No",
            1: "Yes, fully random",
            2: "Yes, first move deals damage",
            3: "Yes, first move deals damage + STAB"
        }],
        tm_hm_movesets: ["Randomize TM/HM Movesets?", UiSwitch],
        tms_hms: ["Randomize TMs/HMs?", UiSwitch],
        abilities_enabled: ["Enabled Abilities", 'abilities_enabled'],
        monsters_enabled: ["Enabled Pokémon", 'monsters_enabled'],
        moves_enabled: ["Enabled Moves", 'moves_enabled']
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
        instant: ["Instant Text?", UiSwitch],
        main: ["Randomize Main Texts?", UiSwitch],
        story: ["Randomize Story Dialogue?", UiSwitch],
    },
    iq: {
        randomize_tactics: ["Randomize Tactics Unlock Levels?", UiSwitch],
        randomize_iq_gain: ["Randomize IQ Gain?", UiSwitch],
        randomize_iq_skills: ["Randomize IQ Skill Unlocks?", UiSwitch],
        randomize_iq_groups: ["Randomize IQ Groups?", UiSwitch],
    },
    quiz: {
        mode: ["Personality Test Starter Settings", UiSelect, {
            0: "Default: Ask for Personality",
            1: "Ask for Personality + Allow Selection",
            2: "Select Manually"
        }],
        randomize: ["Randomize Personality Quiz Questions?", UiSwitch],
        questions: ["Personaility Test Questions:", "To edit the pool of random personality test questions, please use the desktop version of the Randomizer."]
    },
    item: {
        algorithm: ["Item Randomization Algorithm", UiSelect, {
            0: "Balanced",
            1: "Classic",
        }],
        global_items: ["Randomize Treasure Town shop and dungeon rewards?", UiSwitch],
        weights: ["Category Weights", "item_weights"],
    }
}

export const ID_PREFIX = 'r--';

function _s(x) {
    return x.substring(3).replaceAll('-', '.');
}

/**
 * @param {string} id
 * @param {any} newVal
 */
export function updateInConfig(id, newVal) {
    set(self.loadedConfig, _s(id), newVal);
}

/**
 * @param {string} id
 * @param {any} rowIdx
 * @param {number} colIdx
 * @param {any} newVal
 */
export function updateListEnabledInConfig(id, rowIdx, colIdx, newVal) {
    let values = get(self.loadedConfig, _s(id));
    if (newVal) {
        if (!values.includes(parseInt(rowIdx))) {
            values.push(parseInt(rowIdx));
        }
    } else {
        if (values.includes(parseInt(rowIdx))) {
            values = values.filter(function(value, index, arr){
                return value !== parseInt(rowIdx);
            });
        }
    }
    set(self.loadedConfig, _s(id), values);
}

/**
 * @param {string} id
 * @param {any} rowIdx
 * @param {number} colIdx
 * @param {any} newVal
 */
export function updateGenericGridInConfig(id, rowIdx, colIdx, newVal) {
    const config = get(SETTINGS_CONFIG, _s(id))[2];
    const colName = Object.keys(config)[colIdx];
    set(self.loadedConfig, _s(id + '-' + rowIdx + '-' + colName), newVal);
}
