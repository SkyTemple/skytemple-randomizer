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
from skytemple_files.data.str.model import Str
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
        pokemon_string_data = self.static_data.string_index_data.string_blocks[
            "Pokemon Names"
        ]

        status.step(_("Apply 'ActorAndLevelLoader' patch..."))
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied("ActorAndLevelLoader"):
            patcher.apply("ActorAndLevelLoader")

        status.step(_("Randomizing NPC actor list..."))
        mapped_actors = self._randomize_actors(main_string_file, pokemon_string_data)
        mapped_actor_names_by_lang = {}

        for lang, lang_string_file in get_all_string_files(self.rom, self.static_data):
            names_mapped: dict[str, str] = {}
            mapped_actor_names_by_lang[lang] = names_mapped
            for old, new in mapped_actors.items():
                old_base = old % 600
                new_base = new % 600
                old_name = self._get_name(
                    lang_string_file, old_base, pokemon_string_data
                )
                new_name = self._get_name(
                    lang_string_file, new_base, pokemon_string_data
                )
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
                self.rom.setFileByName(
                    f"MESSAGE/{lang.filename}", FileType.STR.serialize(string_file)
                )

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
            # Most NPC texts in the base game are wrapped via [CN:N]...[CR], or [CN:Y]...[CR].
            # Croagunk is the only NPC pokemon that has texts with [CS:E].
            standard_npc_text = re.compile(
                r"\[CS:(N|Y|E)]("
                + "|".join(list(mapped_actor_names.keys()))
                + r")\[CR]"
            )
            # Some place names derived from NPCs are mentioned via [CS:P]...[CR], so we'll replace those as well.
            place_mention_npc_text = re.compile(
                r"\[CS:P](.*)("
                + "|".join(list(mapped_actor_names.keys()))
                + r")(.*)\[CR]"
            )
            # Some [CS:K]...[CR] needs replacing for Kecleon, Chansey, Marowak, Spinda, Chimecho, Mime Jr., Electivire, and all the Pokemon under the Adventure Log.
            # We need to specifically select string block regions to apply this to.
            csk_npc_text = re.compile(
                r"\[CS:K](" + "|".join(list(mapped_actor_names.keys())) + r")\[CR]"
            )
            csk_replace_regions = [
                self.static_data.string_index_data.string_blocks.get(
                    "Job Debriefing Related Strings"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "(MAROWAK-DOJO-STRS-UNMAPPED)"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Spinda's Juice Bar Strings"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "(CHIMECHO-ASM-STR-UNMAPPED)"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Game and Dungeon Hints"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Mime Jr. Spa Strings"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Adventure Log Strings"
                ),
            ]
            # Kecleon needs extra care, because some item long descriptions contain references to the shop (should be replaced) and the Pokemon itself (should not be replaced) at the same time.
            # Instead we replace some of the mentions of the specific text "Kecleon's Shop" (note: things like music track names should not be replaced).
            kecleon_shop_text = {
                # IMPORTANT: match.group(1) should always be Kecleon's name
                "English": re.compile(r"(Kecleon)(?:\[CR])?'s Shop"),
                "French": re.compile(r"Magasins\n?(Kecleon)"),
                "German": re.compile(r"(Kecleon)-Laden"),
                "Italian": re.compile(r"Magazzini\n?(?:\[CS:.])?(Kecleon)"),
                "Spanish": re.compile(r"Tienda\n?(Kecleon)"),
                "Japanese": re.compile(r"(カクレオン)(?:\[CR])?の\n?お?みせ"),
            }
            kecleon_replace_regions = [
                self.static_data.string_index_data.string_blocks.get(
                    "Floor-Wide Status Names+Desc"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Item Long Descriptions"
                ),
            ]
            # Finally, there are plain texts that need replacing for a bunch of Pokemons (typically chapter texts and place names)
            plain_npc_text = re.compile(
                "(" + "|".join(list(mapped_actor_names.keys())) + ")"
            )
            plain_replace_regions = [
                self.static_data.string_index_data.string_blocks.get(
                    "(SPECIAL-EPISODES-STRS-UNMAPPED)"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "(JOURNAL-STRS-UNMAPPED)"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Pokemon WAIT Dialogue"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Ground Map Names"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Dungeon Names (Main)"
                ),
                self.static_data.string_index_data.string_blocks.get(
                    "Dungeon Names (Section)"
                ),
            ]

            for idx, text in enumerate(lang_string_file.strings):
                new_text = standard_npc_text.sub(
                    lambda match: match.expand(
                        f"[CS:{match.group(1)}]{mapped_actor_names[match.group(2)]}[CR]"
                    ),
                    text,
                )
                new_text = place_mention_npc_text.sub(
                    lambda match: match.expand(
                        f"[CS:P]{match.group(1)}{mapped_actor_names[match.group(2)]}{match.group(3)}[CR]"
                    ),
                    new_text,
                )
                if any(
                    block.begin < idx < block.end
                    for block in csk_replace_regions
                    if block is not None
                ):
                    new_text = csk_npc_text.sub(
                        lambda match: match.expand(
                            f"[CS:K]{mapped_actor_names[match.group(1)]}[CR]"
                        ),
                        new_text,
                    )
                if any(
                    block.begin < idx < block.end
                    for block in kecleon_replace_regions
                    if block is not None
                ):
                    new_text = kecleon_shop_text[lang.name_localized].sub(
                        lambda match: match.string[match.start(0) : match.start(1)]
                        + mapped_actor_names[match.group(1)]
                        + match.string[match.end(1) : match.end(0)],
                        new_text,
                    )
                if any(
                    block.begin < idx < block.end
                    for block in plain_replace_regions
                    if block is not None
                ):
                    new_text = plain_npc_text.sub(
                        lambda match: mapped_actor_names[match.group(1)], new_text
                    )
                lang_string_file.strings[idx] = new_text
            self.rom.setFileByName(
                f"MESSAGE/{lang.filename}", FileType.STR.serialize(lang_string_file)
            )

    def _smart_replace_script_mentions(self, mapped_actor_names_by_lang):
        # We don't need to be selective with script text - we should be able to replace all mentions of the NPC names directly.
        # To avoid improper substring matching, we need to construct the regex so that the longer strings are matched first.
        for lang, mapped_actor_names in mapped_actor_names_by_lang.items():
            script_npc_text = re.compile(
                "|".join(sorted(list(mapped_actor_names.keys()), key=len, reverse=True))
            )
            for file_path in get_files_from_rom_with_extension(self.rom, "ssb"):
                if file_path in SKIP_JP_INVALID_SSB:
                    continue
                script = get_script(file_path, self.rom, self.static_data)
                script.constants = [
                    script_npc_text.sub(
                        lambda match: mapped_actor_names[match.group(0)], text
                    )
                    for text in script.constants
                ]
                if len(script.strings) > 0:  # for Japanese this is empty.
                    script.strings[lang.name.lower()] = [
                        script_npc_text.sub(
                            lambda match: mapped_actor_names[match.group(0)], text
                        )
                        for text in script.strings[lang.name.lower()]
                    ]

    def _randomize_actors(self, string_file, pokemon_string_data) -> dict[int, int]:
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
                old_name = self._get_name(
                    string_file, actor.entid % num_entities, pokemon_string_data
                )
                if old_name in mapped_for_names.keys():
                    new_entid = mapped_for_names[old_name]
                    if new_entid >= 1154:
                        new_entid -= u16(num_entities)  # type: ignore
                else:
                    new_entid = choice(
                        get_allowed_md_ids(self.config, True, roster=Roster.NPCS)
                    )
                    # Make it less likely to get duplicates
                    while new_entid in mapped.values() and randrange(0, 4) != 0:
                        new_entid = choice(
                            get_allowed_md_ids(self.config, True, roster=Roster.NPCS)
                        )
                    # Due to the way the string replacing works we don't want anything that previously existed.
                    while (
                        md.get_by_index(new_entid).gender == Gender.INVALID
                        or new_entid % num_entities in old_entid_bases
                    ):
                        new_entid = choice(
                            get_allowed_md_ids(self.config, True, roster=Roster.NPCS)
                        )
                mapped[actor.entid] = new_entid
                mapped_for_names[old_name] = new_entid
                actor.entid = new_entid

        self.rom.setFileByName(
            "BALANCE/actor_list.bin",
            FileType.SIR0.serialize(FileType.SIR0.wrap_obj(actor_list)),
        )
        return mapped

    @staticmethod
    def _get_name(string_file: Str, index: int, pokemon_string_data):
        """Returns a Pokémon name from the string file"""
        return string_file.strings[pokemon_string_data.begin + index]
