#  Copyright 2020-2024 Capypara and the SkyTemple Contributors
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
import re
from random import choice, randrange

from range_typed_integers import u16
from skytemple_files.common.i18n_util import _
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_files_from_rom_with_extension
from skytemple_files.data.md.protocol import Gender
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.util.util import (
    get_main_string_file,
    get_allowed_md_ids,
    get_script,
    replace_text_script,
    replace_text_main,
    clone_missing_portraits,
    get_all_string_files,
    get_pokemon_name,
    SKIP_JP_INVALID_SSB,
    Roster,
)
from skytemple_randomizer.status import Status


class NpcRandomizer(AbstractRandomizer):
    def step_count(self) -> int:
        if self.config["starters_npcs"]["npcs"]:
            return 5
        return 0

    def run(self, status: Status):
        if not self.config["starters_npcs"]["npcs"]:
            return status.done()
        main_lang, main_string_file = get_main_string_file(self.rom, self.static_data)
        pokemon_string_data = self.static_data.string_index_data.string_blocks["Pokemon Names"]

        status.step(_("Apply 'ActorAndLevelLoader' patch..."))
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied("ActorAndLevelLoader"):
            patcher.apply("ActorAndLevelLoader")

        status.step(_("Randomizing NPC actor list..."))
        mapped_actors = self._randomize_actors()
        mapped_actor_names_by_lang = {}

        for lang in self.static_data.string_index_data.languages:
            names_mapped: dict[str, str] = {}
            mapped_actor_names_by_lang[lang] = names_mapped
            for old, new in mapped_actors.items():
                old_base = old % 600
                new_base = new % 600
                old_name = get_pokemon_name(self.rom, self.static_data, old_base, lang)
                new_name = get_pokemon_name(self.rom, self.static_data, new_base, lang)
                names_mapped[old_name] = new_name

        status.step(_("Replacing main text that mentions NPCs..."))
        if self.config["starters_npcs"]["npcs_use_smart_replace"]:
            self._smart_replace_text(mapped_actor_names_by_lang)
        else:
            for lang, string_file in get_all_string_files(self.rom, self.static_data):
                replace_text_main(
                    string_file,
                    mapped_actor_names_by_lang[lang],
                    pokemon_string_data.begin,
                    pokemon_string_data.end,
                )
                self.rom.setFileByName(f"MESSAGE/{lang.filename}", FileType.STR.serialize(string_file))

        status.step(_("Replacing script text that mentions NPCs..."))
        if self.config["starters_npcs"]["npcs_use_smart_replace"]:
            self._smart_replace_script_mentions(mapped_actor_names_by_lang)
        else:
            replace_text_script(self.rom, self.static_data, mapped_actor_names_by_lang)

        status.step(_("Cloning missing NPC portraits..."))
        kao = FileType.KAO.deserialize(self.rom.getFileByName("FONT/kaomado.kao"))
        for new in mapped_actors.values():
            new_base = new % 600
            clone_missing_portraits(kao, new_base - 1)
        self.rom.setFileByName("FONT/kaomado.kao", FileType.KAO.serialize(kao))

        status.done()

    def _smart_replace_text(self, mapped_actor_names_by_lang):
        for lang, lang_string_file in get_all_string_files(self.rom, self.static_data):
            mapped_actor_names = mapped_actor_names_by_lang[lang]
            sorted_actor_names = sorted(list(mapped_actor_names.keys()), key=len, reverse=True)
            # Most NPC texts in the base game are wrapped via [CN:N]...[CR], or [CN:Y]...[CR].
            # Some place names derived from NPCs are mentioned via [CS:P]...[CR], so we'll replace those as well.
            # Croagunk's Swap Shop is mentioned via [CS:E].
            standard_npc_text = re.compile(
                r"\[CS:(N|Y|P|E)]([^\[]*)(" + "|".join(sorted_actor_names) + r")([^\[]*)\[CR]"
            )
            # Some [CS:K]...[CR] needs replacing for Kecleon, Chansey, Marowak, Spinda, Chimecho, Mime Jr., Electivire, and all the Pokemon under the Adventure Log.
            # We need to specifically select string block regions to apply this to.
            csk_npc_text = re.compile(r"\[CS:K]([^\[]*)(" + "|".join(sorted_actor_names) + r")([^\[]*)\[CR]")
            csk_replace_regions = [
                self.static_data.string_index_data.string_blocks.get("Job Debriefing Related Strings (Secondary)"),
                self.static_data.string_index_data.string_blocks.get("Game Trade Strings"),
                self.static_data.string_index_data.string_blocks.get("Spinda's Juice Bar Strings"),
                self.static_data.string_index_data.string_blocks.get("Chimecho Assembly Strings"),
                self.static_data.string_index_data.string_blocks.get("Mime Jr. Spa Strings"),
                self.static_data.string_index_data.string_blocks.get("Adventure Log Entries"),
                self.static_data.string_index_data.string_blocks.get("Floor-Wide Status"),
                self.static_data.string_index_data.string_blocks.get("IQ Skills Descriptions"),
            ]
            # Some pokemons (Kecleon, Shaymin) need extra care, because some item long descriptions contain references to the shop (should be replaced) and the Pokemon itself (should not be replaced) at the same time.
            # Instead we replace some of the mentions of the specific shop names (note: things like music track names should not be replaced).
            shop_texts = {
                # IMPORTANT: match.group(1) should always be the Pokemon name to replace
                "English": [
                    re.compile(r"(Kecleon)(?:\[CR])?'s\sShop"),
                    re.compile(r"(Shaymin)(?:\[CR])?'s\sDelivery\sService"),
                ],
                "French": [
                    re.compile(r"Magasins\s(Kecleon)"),
                    re.compile(r"Service\sde\sLivraison\s(Shaymin)"),
                ],
                "German": [
                    re.compile(r"(Kecleon)-Laden"),
                    re.compile(r"(Shaymin)-Lieferservice"),
                ],
                "Italian": [
                    re.compile(r"Magazzini\s(?:\[CS:.])?(Kecleon)"),
                    re.compile(r"Servizio\sConsegne\s(?:\[CS:.])?(Shaymin)"),
                ],
                "Spanish": [
                    re.compile(r"Repartos\s(Kecleon)"),
                    re.compile(r"Service\sde\sLivraison\s(Shaymin)"),
                ],
                "Japanese": [
                    re.compile(r"(カクレオン)(?:\[CR])?の\s?お?みせ"),
                    re.compile(r"(シェイミ)(?:\[CR])?のたくはいびん"),
                ],
            }
            shop_replace_regions = [
                self.static_data.string_index_data.string_blocks.get("Item Long Descriptions"),
            ]
            # Finally, there are plain texts that need replacing for a bunch of Pokemons (typically chapter texts and place names)
            plain_npc_text = re.compile("(" + "|".join(list(mapped_actor_names.keys())) + ")")
            plain_replace_regions = [
                self.static_data.string_index_data.string_blocks.get("Special Episode Item Handling Strings"),
                self.static_data.string_index_data.string_blocks.get("Chapter and Special Episode Strings"),
                self.static_data.string_index_data.string_blocks.get("Game and Dungeon Hints"),
                self.static_data.string_index_data.string_blocks.get("Ground Map Names"),
                self.static_data.string_index_data.string_blocks.get("Dungeon Names (Main)"),
                self.static_data.string_index_data.string_blocks.get("Dungeon Names (Selection)"),
                self.static_data.string_index_data.string_blocks.get("Dungeon Names (SetDungeonBanner)"),
                self.static_data.string_index_data.string_blocks.get("Dungeon Names (Banner)"),
            ]

            for idx, text in enumerate(lang_string_file.strings):
                string_id = idx + 1
                new_text = standard_npc_text.sub(
                    lambda match: match.expand(
                        f"[CS:{match.group(1)}]{match.group(2)}{mapped_actor_names[match.group(3)]}{match.group(4)}[CR]"
                    ),
                    text,
                )
                if any(block.begin < string_id <= block.end for block in csk_replace_regions if block is not None):
                    new_text = csk_npc_text.sub(
                        lambda match: match.expand(
                            f"[CS:K]{match.group(1)}{mapped_actor_names[match.group(2)]}{match.group(3)}[CR]"
                        ),
                        new_text,
                    )
                if any(block.begin < string_id <= block.end for block in shop_replace_regions if block is not None):
                    for shop_regex in shop_texts[lang.name]:
                        new_text = shop_regex.sub(
                            lambda match: match.string[match.start(0) : match.start(1)]
                            + mapped_actor_names[match.group(1)]
                            + match.string[match.end(1) : match.end(0)],
                            new_text,
                        )
                if any(block.begin < string_id <= block.end for block in plain_replace_regions if block is not None):
                    new_text = plain_npc_text.sub(lambda match: mapped_actor_names[match.group(1)], new_text)
                lang_string_file.strings[idx] = new_text
            self.rom.setFileByName(f"MESSAGE/{lang.filename}", FileType.STR.serialize(lang_string_file))

    def _smart_replace_script_mentions(self, mapped_actor_names_by_lang):
        # We don't need to be selective with script text - we should be able to replace all mentions of the NPC names directly.
        # To avoid improper substring matching, we need to construct the regex so that the longer strings are matched first.
        for lang, mapped_actor_names in mapped_actor_names_by_lang.items():
            script_npc_text = re.compile("|".join(sorted(list(mapped_actor_names.keys()), key=len, reverse=True)))
            for file_path in get_files_from_rom_with_extension(self.rom, "ssb"):
                if file_path in SKIP_JP_INVALID_SSB:
                    continue
                script = get_script(file_path, self.rom, self.static_data)
                script.constants = [
                    script_npc_text.sub(lambda match: mapped_actor_names[match.group(0)], text)
                    for text in script.constants
                ]
                if len(script.strings) > 0:  # for Japanese this is empty.
                    script.strings[lang.name.lower()] = [
                        script_npc_text.sub(lambda match: mapped_actor_names[match.group(0)], text)
                        for text in script.strings[lang.name.lower()]
                    ]

    def _randomize_actors(self) -> dict[int, int]:
        """Returns a dict that maps old entids -> new entids"""
        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName("BALANCE/actor_list.bin")),
            ActorListBin,
        )
        md = FileType.MD.deserialize(self.rom.getFileByName("BALANCE/monster.md"))

        mapped: dict[int, int] = {}
        # We want to map actors with the same name to the same ID
        mapped_for_names: dict[str, u16] = {}
        num_entities = FileType.MD.properties().num_entities
        old_entid_bases = [actor.entid % num_entities for actor in actor_list.list]
        new_entid: u16
        for actor in actor_list.list:
            if actor.entid > 0:
                old_name = get_pokemon_name(
                    self.rom,
                    self.static_data,
                    actor.entid % num_entities,
                    self.static_data.string_index_data.languages[0],
                )
                if old_name in mapped_for_names.keys():
                    new_entid = mapped_for_names[old_name]
                    if new_entid >= 1154:
                        new_entid -= u16(num_entities)  # type: ignore
                else:
                    new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                    # Make it less likely to get duplicates
                    while new_entid in mapped.values() and randrange(0, 4) != 0:
                        new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                    # Due to the way the string replacing works we don't want anything that previously existed.
                    while (
                        md.get_by_index(new_entid).gender == Gender.INVALID
                        or new_entid % num_entities in old_entid_bases
                    ):
                        new_entid = choice(get_allowed_md_ids(self.config, True, roster=Roster.NPCS))
                mapped[actor.entid] = new_entid
                mapped_for_names[old_name] = new_entid
                actor.entid = new_entid

        self.rom.setFileByName(
            "BALANCE/actor_list.bin",
            FileType.SIR0.serialize(FileType.SIR0.wrap_obj(actor_list)),
        )
        return mapped
