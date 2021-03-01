#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
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
import json
import urllib.request
from typing import List, Optional, Dict

from skytemple_files.common.ppmdu_config.data import GAME_REGION_US
from skytemple_files.common.ppmdu_config.script_data import Pmd2ScriptEntity
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import create_file_in_rom, get_binary_from_rom_ppmdu
from skytemple_files.data.md.model import Ability, Md, MdEntry, Gender
from skytemple_files.hardcoded.personality_test_starters import HardcodedPersonalityTestStarters
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_files.script.ssa_sse_sss.actor import SsaActor
from skytemple_files.script.ssa_sse_sss.model import Ssa
from skytemple_files.script.ssa_sse_sss.position import SsaPosition
from skytemple_files.script.ssb.constants import SsbConstant
from skytemple_files.script.ssb.script_compiler import ScriptCompiler
from skytemple_randomizer.config import version, MovesetConfig, DungeonWeatherConfig, DungeonModeConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import get_all_string_files
from skytemple_randomizer.status import Status

STR_EU = 16330
STR_US = 16328
ACTOR_TO_USE = 78
MAP = 'P01P01A'
SCENE = 'enter.sse'
TALK_SCRIPT = 80
TALK_SCRIPT_NAME = f'enter{TALK_SCRIPT}.ssb'
NPC_SECTOR = 0
NPC_X = 13
NPC_Y = 21

TWO_ACTOR_TO_USE = 77
TWO_TALK_SCRIPT = 81
TWO_TALK_SCRIPT_NAME = f'enter{TWO_TALK_SCRIPT}.ssb'
TWO_NPC_SECTOR = 0
TWO_NPC_X = 18
TWO_NPC_Y = 21


def escape(s):
    return s.replace('"', '\\"').replace("'", "\\'")


class ArtistCredits:
    def __init__(self, name: str, actor: Optional[Pmd2ScriptEntity], main_artist: str, other_artists: List[str], id_str: str):
        self.name = name
        self.id_str = id_str
        self.other_artists = other_artists
        self.main_artist = main_artist
        self.actor = actor


class SeedInfo(AbstractRandomizer):
    def step_count(self) -> int:
        return 2

    def run(self, status: Status):
        status.step("Loading Seed Info...")

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
                    direction=self.static_data.script_data.directions__by_name['Down'].ssa_id,
                    x_pos=NPC_X,
                    y_pos=NPC_Y,
                    x_offset=0, y_offset=0
                ),
                script_id=TALK_SCRIPT,
                unkE=-1,
            ))
        already_exists = any(a.script_id == TWO_TALK_SCRIPT for a in layer.actors)
        if not already_exists:
            layer.actors.append(SsaActor(
                scriptdata=self.static_data.script_data,
                actor_id=TWO_ACTOR_TO_USE,
                pos=SsaPosition(
                    scriptdata=self.static_data.script_data,
                    direction=self.static_data.script_data.directions__by_name['Down'].ssa_id,
                    x_pos=TWO_NPC_X,
                    y_pos=TWO_NPC_Y,
                    x_offset=0, y_offset=0
                ),
                script_id=TWO_TALK_SCRIPT,
                unkE=-1,
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
    message_Notice("SkyTemple Randomizer by [CS:A]Parakoopa[CR].\\nVersion:[CS:Z]{version()}[CR]\\nSeed: [CS:C]{self.seed}[CR]");
    
    §l_menu;
    switch ( message_SwitchMenu(0, 1) ) {{
        case menu("Show Settings"):
            ~settings();
            jump @l_menu;
        case menu("Patch Credits"):
            ~patches();
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
        case menu("Starters & More"):
            message_Mail("Randomize Starters?: {self._bool(self.config['starters_npcs']['starters'])}\\nRandomize NPCs and Bosses?: {self._bool(self.config['starters_npcs']['npcs'])}\\nRandomize Shops?: {self._bool(self.config['starters_npcs']['global_items'])}\\nRandomize OW Music?: {self._bool(self.config['starters_npcs']['overworld_music'])}");
            jump @l_settings;
        case menu("Dungeons: General"):
            message_Mail("Mode: {self._dungeon_mode(self.config['dungeons']['mode'])}\\nLayouts and Tilesets?: {self._bool(self.config['dungeons']['layouts'])}\\nRandomize Weather?: {self._weather(self.config['dungeons']['weather'])}\\nRandomize Items?: {self._bool(self.config['dungeons']['items'])}\\nRandomize Pokémon?: {self._bool(self.config['dungeons']['pokemon'])}\\nRandomize Traps?: {self._bool(self.config['dungeons']['traps'])}\\nRandomize Boss Rooms?: {self._bool(self.config['dungeons']['fixed_rooms'])}");
            jump @l_settings;
        case menu("Improvements"):
            message_Mail("Download portraits?: {self._bool(self.config['improvements']['download_portraits'])}\\nApply 'MoveShortcuts'?: {self._bool(self.config['improvements']['patch_moveshortcuts'])}\\nApply 'UnusedDungeonChance'?: {self._bool(self.config['improvements']['patch_unuseddungeonchance'])}\\nApply 'CTC'?: {self._bool(self.config['improvements']['patch_totalteamcontrol'])}");
            jump @l_settings;
        case menu("Pokémon: General"):
            message_Mail("Randomize IQ Groups?: {self._bool(self.config['pokemon']['iq_groups'])}\\nRandomize Abilities?: {self._bool(self.config['pokemon']['abilities'])}\\nRandomize Typings?: {self._bool(self.config['pokemon']['typings'])}\\nRandomize Movesets?: {self._movesets(self.config['pokemon']['movesets'])}\\nBan Unowns?: {self._bool(self.config['pokemon']['ban_unowns'])}");
            jump @l_settings;
        case menu("Pokémon: Abilities"):
            {self._abilities(self.config['pokemon']['abilities_enabled'])}
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
            message_Mail("Randomize Main Texts?: {self._bool(self.config['text']['main'])}\\nRandomize Story Dialogue: {self._bool(self.config['text']['story'])}");
            jump @l_settings;
        {self._dungeon_cases()}
        case menu("Goodbye!"):
        default:
            break;
    }}
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
            message_Notice("SkyTemple Randomizer by [CS:A]Parakoopa[CR].\\nVersion:[CS:Z]{version()}[CR]\\nSeed: [CS:C]{self.seed}[CR]");

            §l_menu;
            switch ( message_SwitchMenu(0, 1) ) {{
                case menu("Artist Credits"):
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
                {self._artist_credits()}
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

        status.done()

    def _bool(self, param):
        if param:
            return "[CS:K]Yes[CR]"
        return "[CS:B]No[CR]"

    def _dungeon_mode(self, param: DungeonModeConfig):
        if param == DungeonModeConfig.FULLY_RANDOM:
            return "[CS:H]Fully random floors[CR]"
        return "[CS:H]Keep floors in a dungeon similar[CR]"

    def _abilities(self, param: List[int]):
        full = ""
        single = "message_Mail(\""
        line = ""
        i = 0
        for i in range(0, len(param)):
            ability_name = Ability(param[i]).print_name
            if i != 0 and i % 2 == 0:
                single += line.strip(", ") + "\\n"
                line = ""
            if i != 0 and i % 18 == 0:
                full += single + "\");"
                single = "message_Mail(\""
            line += escape(ability_name) + ", "
        if i % 18 != 0 and i != 0:
            full += single + "\");"
        return full

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

    def _artist_credits(self):
        credit_map: Dict[str, ArtistCredits] = {}
        credits = ""

        overlay13 = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0013.bin'])
        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )
        starters = HardcodedPersonalityTestStarters.get_partner_md_ids(overlay13, self.static_data)
        partners = HardcodedPersonalityTestStarters.get_player_md_ids(overlay13, self.static_data)
        md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))

        with urllib.request.urlopen("http://sprites.pmdcollab.org/resources/pokemons.json") as url:
            config = json.loads(url.read().decode())

        with urllib.request.urlopen("http://sprites.pmdcollab.org/resources/credits.json") as url:
            credits_config = json.loads(url.read().decode())

        for starter in starters:
            self._process_portrait(credit_map, config, credits_config, starter, md.entries[starter], None)

        for partner in partners:
            self._process_portrait(credit_map, config, credits_config, partner, md.entries[partner], None)

        for actor in actor_list.list:
            if actor.entid > 0:
                self._process_portrait(credit_map, config, credits_config, actor.entid, md.entries[actor.entid], actor)

        credit_map = {k: credit_map[k] for k in sorted(credit_map)}

        for entry in credit_map.values():
            setface = ""
            if entry.actor:
                setface = f"message_SetFaceEmpty({SsbConstant.create_for(entry.actor).name}, FACE_HAPPY, FACE_POS_TOP_L_FACEINW);"
            others = ""
            if entry.other_artists:
                others = list(set(entry.other_artists))
                main = ''
                others_short = others[:3]
                if len(others_short) != len(others):
                    main += ' + more'
                others = f"More Authors: [CS:A]{', '.join(others_short) + main}[CR]"
            credits += f"""
        case menu("{entry.name}"):
            {setface}
            message_Talk("Last Author: [CS:A]{escape(entry.main_artist)}[CR]\\n{escape(others)}\\nsprites.pmdcollab.org/portrait.html?id={escape(entry.id_str)}");
            jump @l_artists;
"""
        return credits

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

    def _process_portrait(self, credit_map: Dict[str, ArtistCredits], config, credits_config, mdidx, md: MdEntry, actor: Optional[Pmd2ScriptEntity]):
        pokedex_number = md.national_pokedex_number
        forms_to_try = ['0000']
        if md.gender == Gender.FEMALE:
            forms_to_try.insert(0, '0000f')
        if mdidx == 279:  # Celebi Shiny
            forms_to_try.insert(0, '0000s')
        if f'{pokedex_number:04}' in config and '0000' in config[f'{pokedex_number:04}']['forms']:
            decided_form = None
            for form in forms_to_try:
                if form in config[f'{pokedex_number:04}']['forms']:
                    decided_form = config[f'{pokedex_number:04}']['forms'][form]
                    break
            if not decided_form:
                return
            name = config[f'{pokedex_number:04}']['name'] + " (" + decided_form['name'] + ")"
            main_artist, other_artists = self._resolve_credits(credits_config, reversed(decided_form['credits']))
            credit_map[name] = ArtistCredits(
                name, actor, main_artist, other_artists, f'{pokedex_number:04}'
            )

    def _resolve_credits(self, credits_config, credits):
        main = None
        others = []
        for credit in credits:
            artist_id = credit[1]
            artist_credits = credits_config[str(artist_id)]
            name = artist_credits['name']
            if name == "":
                name = artist_credits['id']
            link = ""
            if artist_credits['contact'] != "":
                link = f" ({artist_credits['contact']})"
            if main is None:
                main = f'{name}{link}'
            else:
                others.append(name)
        return main, others
