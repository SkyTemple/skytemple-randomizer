#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
import traceback
from numbers import Number
from typing import Mapping, Sequence, Tuple, Dict

from range_typed_integers import u16, i16
from skytemple_files.common import string_codec
from skytemple_files.common.ppmdu_config.data import GAME_REGION_US
from skytemple_files.common.spritecollab.schema import Credit
from skytemple_files.common.string_codec import can_be_encoded
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import create_file_in_rom
from skytemple_files.patch.patches import Patcher
from skytemple_files.script.ssa_sse_sss.actor import SsaActor
from skytemple_files.script.ssa_sse_sss.model import Ssa
from skytemple_files.script.ssa_sse_sss.position import SsaPosition
from skytemple_files.script.ssb.script_compiler import ScriptCompiler
from skytemple_randomizer.config import version, MovesetConfig, DungeonWeatherConfig, DungeonModeConfig, ItemAlgorithm
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.special import fun
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.spritecollab import portrait_credits, sprite_credits
from skytemple_randomizer.status import Status

STR_EU = 16330
STR_US = 16328
ACTOR_TO_USE = u16(78)
MAP = 'P01P01A'
SCENE = 'enter.sse'
TALK_SCRIPT = i16(80)
TALK_SCRIPT_NAME = f'enter{TALK_SCRIPT}.ssb'
NPC_SECTOR = 0
NPC_X = u16(5)
NPC_Y = u16(21)

TWO_ACTOR_TO_USE = u16(77)
TWO_TALK_SCRIPT = i16(81)
TWO_TALK_SCRIPT_NAME = f'enter{TWO_TALK_SCRIPT}.ssb'
TWO_NPC_SECTOR = 0
TWO_NPC_X = u16(10)
TWO_NPC_Y = u16(21)

THREE_ACTOR_TO_USE = u16(76)
THREE_TALK_SCRIPT = i16(83)
THREE_TALK_SCRIPT_NAME = f'enter{THREE_TALK_SCRIPT}.ssb'
THREE_NPC_SECTOR = 0
THREE_NPC_X = u16(15)
THREE_NPC_Y = u16(21)

FOUR_ACTOR_TO_USE = u16(75)
FOUR_TALK_SCRIPT = i16(84)
FOUR_TALK_SCRIPT_NAME = f'enter{FOUR_TALK_SCRIPT}.ssb'
FOUR_NPC_SECTOR = 0
FOUR_NPC_X = u16(20)
FOUR_NPC_Y = u16(21)


def escape(s):
    """
    Returns a modified version of s that can be written to an EoS script.
    Quotes and double quotes are escaped with '\'. Characters that cannot be represented
    using the PMD font are removed.
    """
    new_str = s.replace('"', '\\"').replace("'", "\\'")
    new_str = "".join([c for c in new_str if can_be_encoded(c)])
    return new_str


class SeedInfo(AbstractRandomizer):
    def step_count(self) -> int:
        return 2

    def run(self, status: Status):
        status.step("Loading Seed Info...")
        string_codec.init()

        langs = list(get_all_string_files(self.rom, self.static_data))
        str_offset = STR_EU
        if self.static_data.game_region == GAME_REGION_US:
            str_offset = STR_US

        for lang, string_file in langs:
            string_file.strings[str_offset] = f"""Randomized with SkyTemple Randomizer.
Version:[CS:Z]{version()}[CR]
Seed: [CS:C]{self.seed}[CR]

[CS:H]PLEASE NOTE:[CR]
This seed will only produce the same output
when used with the exact same version
and configuration of the randomizer that
was used.
You can see the configuration of the last
randomization applied by talking to the NPC
on Crossroads."""

        for lang, string_file in langs:
            self.rom.setFileByName(f'MESSAGE/{lang.filename}', FileType.STR.serialize(string_file))

        status.step("Placing Info NPC...")
        # Place NPC in scene
        scene: Ssa = FileType.SSA.deserialize(self.rom.getFileByName(f'SCRIPT/{MAP}/{SCENE}'))
        layer = scene.layer_list[0]
        already_exists = any(a.script_id == TALK_SCRIPT for a in layer.actors)
        if not already_exists:
            layer.actors.append(SsaActor(
                scriptdata=self.static_data.script_data,
                actor_id=ACTOR_TO_USE,
                pos=SsaPosition(
                    scriptdata=self.static_data.script_data,
                    direction=u16(self.static_data.script_data.directions__by_name['Down'].ssa_id),
                    x_pos=NPC_X,
                    y_pos=NPC_Y,
                    x_offset=u16(0), y_offset=u16(0)
                ),
                script_id=TALK_SCRIPT,
                unkE=i16(-1),
            ))
        already_exists = any(a.script_id == TWO_TALK_SCRIPT for a in layer.actors)
        if not already_exists:
            layer.actors.append(SsaActor(
                scriptdata=self.static_data.script_data,
                actor_id=TWO_ACTOR_TO_USE,
                pos=SsaPosition(
                    scriptdata=self.static_data.script_data,
                    direction=u16(self.static_data.script_data.directions__by_name['Down'].ssa_id),
                    x_pos=TWO_NPC_X,
                    y_pos=TWO_NPC_Y,
                    x_offset=u16(0), y_offset=u16(0)
                ),
                script_id=TWO_TALK_SCRIPT,
                unkE=i16(-1),
            ))
        already_exists = any(a.script_id == THREE_TALK_SCRIPT for a in layer.actors)
        if not already_exists:
            layer.actors.append(SsaActor(
                scriptdata=self.static_data.script_data,
                actor_id=THREE_ACTOR_TO_USE,
                pos=SsaPosition(
                    scriptdata=self.static_data.script_data,
                    direction=u16(self.static_data.script_data.directions__by_name['Down'].ssa_id),
                    x_pos=THREE_NPC_X,
                    y_pos=THREE_NPC_Y,
                    x_offset=u16(0), y_offset=u16(0)
                ),
                script_id=THREE_TALK_SCRIPT,
                unkE=i16(-1),
            ))
        already_exists = any(a.script_id == FOUR_TALK_SCRIPT for a in layer.actors)
        if not already_exists:
            layer.actors.append(SsaActor(
                scriptdata=self.static_data.script_data,
                actor_id=FOUR_ACTOR_TO_USE,
                pos=SsaPosition(
                    scriptdata=self.static_data.script_data,
                    direction=u16(self.static_data.script_data.directions__by_name['Down'].ssa_id),
                    x_pos=FOUR_NPC_X,
                    y_pos=FOUR_NPC_Y,
                    x_offset=u16(0), y_offset=u16(0)
                ),
                script_id=FOUR_TALK_SCRIPT,
                unkE=i16(-1),
            ))
        self.rom.setFileByName(f'SCRIPT/{MAP}/{SCENE}', FileType.SSA.serialize(scene))
        # Fill talk script 1
        exps = f"""
def 0 {{
    with (actor ACTOR_TALK_MAIN) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_TALK_SUB) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_ATTENDANT1) {{
        SetAnimation(2);
    }}

    message_SetFace(ACTOR_NPC_TEST010, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);
    message_Talk(" This ROM has been randomized\\nwith the SkyTemple Randomizer!");
    message_ResetActor();
    message_Notice("SkyTemple Randomizer by [CS:A]Capypara[CR].\\nVersion:[CS:Z]{escape(version())}[CR]\\nSeed: [CS:C]{escape(str(self.seed))}[CR]");

    §l_menu;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("Show Settings"):
            ~settings();
            jump @l_menu;
        case menu("Goodbye!"):
        default:
            break;
    }}

    JumpCommon(CORO_END_TALK);
}}

macro settings() {{
    §l_settings;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("General"):
            message_Mail("Randomize Starters?: {self._bool(self.config['starters_npcs']['starters'])}\\nRandomize NPCs and Bosses?: {self._bool(self.config['starters_npcs']['npcs'])}\\nRandomize OW Music?: {self._bool(self.config['starters_npcs']['overworld_music'])}\\nRandomize Top-Menu Music?: {self._bool(self.config['starters_npcs']['topmenu_music'])}\\nRandomize Explorer Rank Unlocks?: {self._bool(self.config['starters_npcs']['explorer_rank_unlocks'])}\\nRandomize Explorer Rank Rewards?: {self._bool(self.config['starters_npcs']['explorer_rank_rewards'])}\\Use Native File Handlers: {self._bool(self.config['starters_npcs']['native_file_handlers'])}");
            jump @l_settings;
        case menu("Items"):
            message_Mail("Item Randomization Algorithm: {self._item_algo(self.config['item']['algorithm'])}\\nRandomize Shops?: {self._bool(self.config['item']['global_items'])}\\n");
            message_Mail("Next are the item category weights...");
            message_Mail("{self._item_weights(self.config['item']['weights'])}");
            jump @l_settings;
        case menu("Dungeons: General"):
            message_Mail("Mode: {self._dungeon_mode(self.config['dungeons']['mode'])}\\nLayouts and Tilesets?: {self._bool(self.config['dungeons']['layouts'])}\\nRandomize Weather?: {self._weather(self.config['dungeons']['weather'])}\\nRandomize Items?: {self._bool(self.config['dungeons']['items'])}\\nRandomize Pokémon?: {self._bool(self.config['dungeons']['pokemon'])}\\nRandomize Traps?: {self._bool(self.config['dungeons']['traps'])}\\nRandomize Boss Rooms?: {self._bool(self.config['dungeons']['fixed_rooms'])}\\Max Sticky Item Chance: {self.config['dungeons']['max_sticky_chance']}%\\nMax Monster House Chance: {self.config['dungeons']['max_mh_chance']}%\\nRandomize Floor count (down): {self.config['dungeons']['min_floor_change_percent']}%\\nRandomize Floor count (up): {self.config['dungeons']['max_floor_change_percent']}%");
            jump @l_settings;
        case menu("Improvements"):
            message_Mail("Download portraits?: {self._bool(self.config['improvements']['download_portraits'])}\\nApply 'MoveShortcuts'?: {self._bool(self.config['improvements']['patch_moveshortcuts'])}\\nApply 'UnusedDungeonChance'?: {self._bool(self.config['improvements']['patch_unuseddungeonchance'])}\\nApply 'CTC'?: {self._bool(self.config['improvements']['patch_totalteamcontrol'])}\\nApply 'FixMemorySoftlock'?: {self._bool(self.config['improvements']['patch_fixmemorysoftlock'])}");
            jump @l_settings;
        case menu("Pokémon: General"):
            message_Mail("Randomize IQ Groups?: {self._bool(self.config['pokemon']['iq_groups'])}\\nRandomize Abilities?: {self._bool(self.config['pokemon']['abilities'])}\\nRandomize Typings?: {self._bool(self.config['pokemon']['typings'])}\\nRandomize Level-Up Movesets?: {self._movesets(self.config['pokemon']['movesets'])}\\nRandomize TM/HM Movesets?: {self._bool(self.config['pokemon']['tm_hm_movesets'])}\\nRandomize TM/HMs?: {self._bool(self.config['pokemon']['tms_hms'])}");
            jump @l_settings;
        case menu("Locations (First)"):
            message_Mail("Randomize?: {self._bool(self.config['locations']['randomize'])}");
            {self._locs_chaps(self.config['locations']['first'])}
            jump @l_settings;
        case menu("Locations (Second)"):
            message_Mail("Randomize?: {self._bool(self.config['locations']['randomize'])}");
            {self._locs_chaps(self.config['locations']['second'])}
            jump @l_settings;
        case menu("Chapters"):
            message_Mail("Randomize?: {self._bool(self.config['chapters']['randomize'])}");
            {self._locs_chaps(self.config['chapters']['text'])}
            jump @l_settings;
        case menu("Text"):
            message_Mail("Randomize Main Texts?: {self._bool(self.config['text']['main'])}\\nRandomize Story Dialogue: {self._bool(self.config['text']['story'])}\\nInstant Text?: {self._bool(self.config['text']['instant'])}");
            jump @l_settings;
        case menu("Tactics and IQ"):
            message_Mail("Randomize Tactics Unlock Levels?: {self._bool(self.config['iq']['randomize_tactics'])}\\nRandomize IQ Gain?: {self._bool(self.config['iq']['randomize_iq_gain'])}\\nRandomize IQ Skill Unlocks?: {self._bool(self.config['iq']['randomize_iq_skills'])}\\nRandomize IQ Groups?: {self._bool(self.config['iq']['randomize_iq_groups'])}");
            jump @l_settings;
        {self._dungeon_cases()}
        case menu("Goodbye!"):
        default:
            break;
    }}
}}
"""
        script, _ = ScriptCompiler(self.static_data).compile_explorerscript(
            exps, 'script.exps', lookup_paths=[]
        )

        script_fn = f'SCRIPT/{MAP}/{TALK_SCRIPT_NAME}'
        script_sera = FileType.SSB.serialize(script, static_data=self.static_data)
        try:
            create_file_in_rom(self.rom, script_fn, script_sera)
        except FileExistsError:
            self.rom.setFileByName(script_fn, script_sera)

        exps = f"""
def 0 {{
    with (actor ACTOR_TALK_MAIN) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_TALK_SUB) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_ATTENDANT1) {{
        SetAnimation(2);
    }}

    message_SetFace(ACTOR_NPC_TEST009, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);
    message_Talk(" This ROM has been randomized\\nwith the SkyTemple Randomizer!");
    message_ResetActor();
    message_Notice("SkyTemple Randomizer by [CS:A]Capypara[CR].\\nVersion:[CS:Z]{escape(version())}[CR]\\nSeed: [CS:C]{escape(str(self.seed))}[CR]");

    §l_menu;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("Portrait Credits"):
            ~artists();
            jump @l_menu;
        case menu("Goodbye!"):
        default:
            break;
    }}

    JumpCommon(CORO_END_TALK);
}}

macro artists() {{
    §l_artists;
    switch ( message_SwitchMenu(0, 1) ) {{
        {self._artist_credits(portrait_credits())}
        case menu("Goodbye!"):
        default:
            break;
    }}
    message_ResetActor();
}}
"""
        script, _ = ScriptCompiler(self.static_data).compile_explorerscript(
            exps, 'script.exps', lookup_paths=[]
        )

        script_fn = f'SCRIPT/{MAP}/{TWO_TALK_SCRIPT_NAME}'
        script_sera = FileType.SSB.serialize(script, static_data=self.static_data)
        try:
            create_file_in_rom(self.rom, script_fn, script_sera)
        except FileExistsError:
            self.rom.setFileByName(script_fn, script_sera)

        if not fun.is_fun_allowed():
            exps = f"""
def 0 {{
    with (actor ACTOR_TALK_MAIN) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_TALK_SUB) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_ATTENDANT1) {{
        SetAnimation(2);
    }}

    message_SetFace(ACTOR_NPC_TEST008, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);
    message_Talk(" This ROM has been randomized\\nwith the SkyTemple Randomizer!");
    message_ResetActor();
    message_Notice("SkyTemple Randomizer by [CS:A]Capypara[CR].\\nVersion:[CS:Z]{escape(version())}[CR]\\nSeed: [CS:C]{escape(str(self.seed))}[CR]");

    §l_menu;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("Sprite Credits"):
            ~artists();
            jump @l_menu;
        case menu("Goodbye!"):
        default:
            break;
    }}

    JumpCommon(CORO_END_TALK);
}}

macro artists() {{
    §l_artists;
    switch ( message_SwitchMenu(0, 1) ) {{
        {self._artist_credits(sprite_credits())}
        case menu("Goodbye!"):
        default:
            break;
    }}
    message_ResetActor();
}}
    """

        else:
            exps = f"""
def 0 {{
    with (actor ACTOR_TALK_MAIN) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_TALK_SUB) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_ATTENDANT1) {{
        SetAnimation(2);
    }}

    message_SetFace(ACTOR_NPC_TEST008, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);
    message_Talk(" :)");

    JumpCommon(CORO_END_TALK);
}}
                """

        script, _ = ScriptCompiler(self.static_data).compile_explorerscript(
            exps, 'script.exps', lookup_paths=[]
        )

        script_fn = f'SCRIPT/{MAP}/{THREE_TALK_SCRIPT_NAME}'
        script_sera = FileType.SSB.serialize(script, static_data=self.static_data)
        try:
            create_file_in_rom(self.rom, script_fn, script_sera)
        except FileExistsError:
            self.rom.setFileByName(script_fn, script_sera)

        exps = f"""
def 0 {{
    with (actor ACTOR_TALK_MAIN) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_TALK_SUB) {{
        ExecuteCommon(CORO_LIVES_REPLY_NORMAL, 0);
    }}
    with (actor ACTOR_ATTENDANT1) {{
        SetAnimation(2);
    }}

    message_SetFace(ACTOR_NPC_TEST007, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);
    message_Talk(" This ROM has been randomized\\nwith the SkyTemple Randomizer!");
    message_ResetActor();
    message_Notice("SkyTemple Randomizer by [CS:A]Capypara[CR].\\nVersion:[CS:Z]{escape(version())}[CR]\\nSeed: [CS:C]{escape(str(self.seed))}[CR]");

    §l_menu;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("Patch Credits"):
            ~patches();
            jump @l_menu;
        case menu("Goodbye!"):
        default:
            break;
    }}

    JumpCommon(CORO_END_TALK);
}}

macro patches() {{
    §l_patches;
    switch ( message_SwitchMenu(0, 1) ) {{
        {self._patch_credits()}
        case menu("Goodbye!"):
        default:
            break;
    }}
}}  
"""
        script, _ = ScriptCompiler(self.static_data).compile_explorerscript(
            exps, 'script.exps', lookup_paths=[]
        )

        script_fn = f'SCRIPT/{MAP}/{FOUR_TALK_SCRIPT_NAME}'
        script_sera = FileType.SSB.serialize(script, static_data=self.static_data)
        try:
            create_file_in_rom(self.rom, script_fn, script_sera)
        except FileExistsError:
            self.rom.setFileByName(script_fn, script_sera)

        status.done()

    def _bool(self, param):
        if param:
            return "[CS:K]Yes[CR]"
        return "[CS:B]No[CR]"

    def _dungeon_mode(self, param: DungeonModeConfig):
        if param == DungeonModeConfig.FULLY_RANDOM:
            return "[CS:H]Fully random floors[CR]"
        return "[CS:H]Keep floors in a dungeon similar[CR]"

    def _item_algo(self, param: ItemAlgorithm):
        if param == ItemAlgorithm.CLASSIC:
            return "[CS:H]Classic[CR]"
        return "[CS:H]Balanced[CR]"

    def _item_weights(self, param: Dict[int, Number]):
        out = ""
        for idx, weight_multi in param.items():
            cat_name = self.static_data.dungeon_data.item_categories[idx].name
            out += f"> {cat_name}: {weight_multi}\\n"
        return out.rstrip()

    def _locs_chaps(self, param: str):
        full = ""
        single = "message_Mail(\""
        line = ""
        i = 0
        for i, entry in enumerate(param.splitlines()):
            if i != 0 and i % 2 == 0:
                single += line.strip(", ") + "\\n"
                line = ""
            if i != 0 and i % 18 == 0:
                full += single + "\");"
                single = "message_Mail(\""
            line += escape(entry) + ", "
        if i % 18 != 0 and i != 0:
            full += single + "\");"
        return full

    def _movesets(self, param: MovesetConfig):
        if param == MovesetConfig.FULLY_RANDOM:
            return "[CS:H]Yes, fully random[CR]"
        if param == MovesetConfig.FIRST_DAMAGE:
            return "[CS:H]Yes, first move deals damage[CR]"
        if param == MovesetConfig.FIRST_STAB:
            return "[CS:H]Yes, first move deals damage + STAB[CR]"
        return "[CS:B]No[CR]"

    def _weather(self, param: DungeonWeatherConfig):
        if param == DungeonWeatherConfig.ONLY_RANDOM:
            return "[CS:H]Fully random every visit[CR]"
        if param == DungeonWeatherConfig.SHUFFLED:
            return "[CS:H]Pre-generated[CR]"
        if param == DungeonWeatherConfig.SHUFFLED_LOWER_BAD_CHANCE:
            return "[CS:H]Pre-generated (less damage)[CR]"
        return "[CS:B]No[CR]"

    def _dungeon_cases(self):
        cases = ""
        for dungeon_id, settings in self.config['dungeons']['settings'].items():
            dungeon_name = self.static_data.dungeon_data.dungeons[dungeon_id].name
            cases += f"""
        case menu("D{dungeon_id:03}: {dungeon_name}"):
            message_Mail("Randomize?: {self._bool(settings['randomize'])}\\nAllow Monster Houses?: {self._bool(settings['monster_houses'])}\\nRandomize Weather?: {self._bool(settings['randomize_weather'])}\\nRandomize IQ?: {self._bool(settings['enemy_iq'])}\\nUnlock?: {self._bool(settings['unlock'])}");
            jump @l_settings;
"""
        return cases

    def _artist_credits(self, credits: Mapping[Tuple[str, str], Sequence[Credit]]):
        if fun.is_fun_allowed():
            return fun.get_artist_credits(self.rom, self.static_data)

        out_credits = ""
        try:
            for (name, monster_id), entry in credits.items():
                others = ""
                if len(entry) > 1:
                    raw_others = entry[1:]
                    main = ''
                    others_short = raw_others[:3]
                    if len(others_short) != len(others):
                        main += ' + more'
                    others_short_f = [parse_credit(x, False) for x in others_short]
                    others = f"More Authors: [CS:A]{', '.join(others_short_f) + main}[CR]"
                out_credits += f"""
        case menu("{name}"):
            message_Talk("Main Author: [CS:A]{escape(parse_credit(entry[0], True))}[CR]\\n{escape(others)}\\nsprites.pmdcollab.org/#/{escape(monster_id)}");
            jump @l_artists;
"""
        except:
            traceback.print_exc()
            return """
        case menu("Error!"):
            message_Mail("Sorry! There was a critical error while \\ncollecting the data during randomization!\\nPlease visit sprites.pmdcollab.org for credits!");
            jump @l_artists;
"""
        return out_credits

    def _patch_credits(self):
        credits = ""
        for patch in Patcher(self.rom, self.static_data).list():
            try:
                if patch.is_applied(self.rom, self.static_data):
                    desc = patch.description.replace('\n', '\\n')
                    credits += f"""
        case menu("{patch.name}"):
            message_Mail("[CS:A]{escape(patch.name)}[CR]\\nby [CS:A]{escape(patch.author)}[CR]\\n\\n{escape(desc)}");
            jump @l_patches; 
"""
            except NotImplementedError:
                pass
        return credits

    @staticmethod
    def printable(s: str):
        try:
            s.encode(string_codec.PMD2_STR_ENCODER)
        except Exception:
            return False
        return True


def parse_credit(credit: Credit, long: bool) -> str:
    artist_name = credit['id']
    if credit['name'] is not None:
        artist_name = credit['name']
    elif credit['discordHandle'] is not None:
        artist_name = credit['discordHandle']
    if long:
        link = ''
        if credit['contact'] is not None:
            link = f" ({credit['contact']})"
        return f'{artist_name}{link}'
    return artist_name
