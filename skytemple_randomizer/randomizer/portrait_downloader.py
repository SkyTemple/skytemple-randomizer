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
import asyncio
import sys
import traceback
from typing import List, Tuple, Coroutine

from ndspy.rom import NintendoDSRom
from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.spritecollab.client import SpriteCollabSession
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom, MONSTER_BIN, chunks
from skytemple_files.data.md.protocol import Gender, MdEntryProtocol, ShadowSize
from skytemple_files.data.sprconf.handler import SprconfType, SPRCONF_FILENAME
from skytemple_files.graphics.chara_wan.model import WanFile
from skytemple_files.graphics.kao.protocol import KaoProtocol
from skytemple_files.hardcoded.personality_test_starters import HardcodedPersonalityTestStarters
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher

from skytemple_randomizer.config import Global, RandomizerConfig
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.randomizer.special import fun
from skytemple_randomizer.spritecollab import sprite_collab, get_details_and_portraits, get_sprites
from skytemple_randomizer.status import Status

GROUND_BIN = 'MONSTER/m_ground.bin'
ATTACK_BIN = 'MONSTER/m_attack.bin'


class PortraitDownloader(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str, frontend: AbstractFrontend):
        super().__init__(config, rom, static_data, seed, frontend)
        self._debugs: List[Tuple[str, str, str, str, str]] = []

        self.monster_bin = FileType.BIN_PACK.deserialize(rom.getFileByName(MONSTER_BIN))
        self.monster_ground_bin = FileType.BIN_PACK.deserialize(rom.getFileByName(GROUND_BIN))
        self.monster_attack_bin = FileType.BIN_PACK.deserialize(rom.getFileByName(ATTACK_BIN))
        self.current = 0
        self.total = "?"

    def step_count(self) -> int:
        if self.config['improvements']['download_portraits']:
            if fun.is_fun_allowed():
                return 1
            try:
                actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
                    FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
                )
                actors = len(actor_list.list)
            except ValueError:
                actors = len(self.static_data.script_data.level_entities)
            overlay13 = get_binary_from_rom(self.rom, self.static_data.bin_sections.overlay13)
            starters = HardcodedPersonalityTestStarters.get_partner_md_ids(overlay13, self.static_data)
            partners = HardcodedPersonalityTestStarters.get_player_md_ids(overlay13, self.static_data)
            total = actors + len(starters) + len(partners)
            self.total = str(total)
            return total
        return 0

    def run(self, status: Status):
        if not self.config['improvements']['download_portraits']:
            return status.done()

        status.step("Apply 'ActorAndLevelLoader' patch...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('ActorAndLevelLoader'):
            patcher.apply('ActorAndLevelLoader')

        overlay13 = get_binary_from_rom(self.rom, self.static_data.bin_sections.overlay13)
        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )
        starters = HardcodedPersonalityTestStarters.get_partner_md_ids(overlay13, self.static_data)
        partners = HardcodedPersonalityTestStarters.get_player_md_ids(overlay13, self.static_data)
        md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))
        kao = FileType.KAO.deserialize(self.rom.getFileByName('FONT/kaomado.kao'))
        sprconf = FileType.SPRCONF.load(self.rom)

        status.step(f"Downloading portraits and sprites... {self.current}/{self.total}")
        if fun.is_fun_allowed():
            fun.replace_portraits(self.rom, self.static_data)
            return status.done()

        async def loop_task():
            task_params = []
            for actor in actor_list.list:
                if actor.entid > 0:
                    task_params.append({
                        "kaos": kao,
                        "mdidx": actor.entid,
                        "md": md.entries[actor.entid],
                        "sprconf": sprconf,
                        "status": status,
                        "sprites": False
                    })

            for starter in starters:
                task_params.append({
                    "kaos": kao,
                    "mdidx": starter,
                    "md": md.entries[starter],
                    "sprconf": sprconf,
                    "status": status,
                    "sprites": True
                })

            for partner in partners:
                task_params.append({
                    "kaos": kao,
                    "mdidx": partner,
                    "md": md.entries[partner],
                    "sprconf": sprconf,
                    "status": status,
                    "sprites": True
                })

            i = 0

            for chunk in chunks(task_params, 30):
                async with sprite_collab() as sc:
                    tasks: List[Coroutine] = []
                    for task_param_kwargs in chunk:
                        tasks.append(self._import_portrait(sc, **task_param_kwargs))

                    await asyncio.gather(*tasks, return_exceptions=False)

        asyncio.run(loop_task())

        self.rom.setFileByName('FONT/kaomado.kao', FileType.KAO.serialize(kao))
        self.rom.setFileByName('BALANCE/monster.md', FileType.MD.serialize(md))
        self.rom.setFileByName(SPRCONF_FILENAME, FileType.SPRCONF.serialize(sprconf))
        self.rom.setFileByName(MONSTER_BIN, FileType.BIN_PACK.serialize(self.monster_bin))
        self.rom.setFileByName(GROUND_BIN, FileType.BIN_PACK.serialize(self.monster_ground_bin))
        self.rom.setFileByName(ATTACK_BIN, FileType.BIN_PACK.serialize(self.monster_attack_bin))

        def add_rows():
            if Global.main_builder:
                o = Global.main_builder.get_object('store_debug_portraits')
                o.clear()
                for row in self._debugs:
                    o.append(row)

        self.frontend.idle_add(add_rows)

        status.done()

    def _match_form(self, mdidx: int, pokedex_number: int, gender_id: int) -> List[Tuple[int, str]]:
        """
        Returns the monster ID and form paths (in preferred order) for this entry from the ROM.
        Maps some special cases in the vanilla ROM to special mon, if the expected dex
        entry matches.
        """
        paths = []

        # Unowns
        if 202 <= mdidx <= 228 and pokedex_number == 201:
            paths.append((pokedex_number, f"{(mdidx-201):04}"))

        # Castform Snowy
        if mdidx in (380, 980) and pokedex_number == 351:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0003/0000/0002"))
            else:
                paths.append((pokedex_number, "0003/0000/0001"))
            paths.append((pokedex_number, "0003"))

        # Castform Sunny
        if mdidx in (381, 981) and pokedex_number == 351:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Castform Rainy
        if mdidx in (382, 982) and pokedex_number == 351:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0002/0000/0002"))
            else:
                paths.append((pokedex_number, "0002/0000/0001"))
            paths.append((pokedex_number, "0002"))

        # Shaymin SKy
        if mdidx in (535, 1135) and pokedex_number == 492:
            paths.append((pokedex_number, "0001"))

        # Cherrim Sunshine
        if mdidx in (461, 1061) and pokedex_number == 421:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Giratina Origin
        if mdidx in (536, 1136) and pokedex_number == 487:
            paths.append((pokedex_number, "0001"))

        # Deoxys Attack
        if mdidx in (419, 1019) and pokedex_number == 386:
            paths.append((pokedex_number, "0001"))

        # Deoxys Defense
        if mdidx in (420, 1020) and pokedex_number == 386:
            paths.append((pokedex_number, "0002"))

        # Deoxys Speed
        if mdidx in (421, 1021) and pokedex_number == 386:
            paths.append((pokedex_number, "0003"))

        # Burmy Sand
        if mdidx in (447, 1047) and pokedex_number == 412:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Burmy Trash
        if mdidx in (449, 1049) and pokedex_number == 412:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0002/0000/0002"))
            else:
                paths.append((pokedex_number, "0002/0000/0001"))
            paths.append((pokedex_number, "0002"))

        # Wormadam Sand
        if mdidx in (450, 1050) and pokedex_number == 413:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Wormadam Trash
        if mdidx in (452, 1052) and pokedex_number == 413:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0002/0000/0002"))
            else:
                paths.append((pokedex_number, "0002/0000/0001"))
            paths.append((pokedex_number, "0002"))

        # Shellos East
        if mdidx in (462, 1062) and pokedex_number == 422:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Gastradon East
        if mdidx in (464, 1064) and pokedex_number == 423:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        # Celebi Shiny
        if mdidx in (279, 879) and pokedex_number == 251:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0000/0001/0002"))
            else:
                paths.append((pokedex_number, "0000/0001/0001"))
            paths.append((pokedex_number, "0000/0001"))

        # Kecleon Purple
        if mdidx in (384, 984) and pokedex_number == 352:
            if gender_id == Gender.FEMALE.value:
                paths.append((pokedex_number, "0001/0000/0002"))
            else:
                paths.append((pokedex_number, "0001/0000/0001"))
            paths.append((pokedex_number, "0001"))

        if gender_id == Gender.FEMALE.value:
            paths.append((pokedex_number, "0000/0000/0002"))
        else:
            paths.append((pokedex_number, "0000/0000/0001"))
        paths.append((pokedex_number, ""))
        return paths

    async def _import_portrait(
            self,
            sc: SpriteCollabSession,
            kaos: KaoProtocol,
            mdidx: int,
            md: MdEntryProtocol,
            sprconf: SprconfType,
            status: Status,
            sprites: bool = False
    ):
        pokedex_number = md.national_pokedex_number
        form_id = '???'
        poke_name = '???'
        form_name = '???'

        forms = self._match_form(mdidx, pokedex_number, md.gender)

        try:
            form_id = forms[0][1]
            result = await get_details_and_portraits(sc, forms)
            if result is not None:
                details, portraits = result
                form_id = details.form_path
                poke_name = details.monster_name
                form_name = details.full_form_name.replace(f"{poke_name} ", "")

                for subindex, image in enumerate(portraits):
                    if image is not None:
                        kaos.set(mdidx - 1, subindex, image)
                self._debugs.append((f'{pokedex_number:04}', poke_name, form_id, form_name, '✓'))
            else:
                self._debugs.append((f'{pokedex_number:04}', poke_name, '-', '-', '-'))

            if sprites:
                spr_result = await get_sprites(sc, forms)
                if spr_result is not None:
                    wan_file, pmd2_sprite, shadow_size_id = spr_result
                    pmd2_sprite.id = md.sprite_index
                    monster, ground, attack = FileType.WAN.CHARA.split_wan(wan_file)
                    # update sprite
                    self.save_monster_monster_sprite(md.sprite_index, monster)
                    self.save_monster_ground_sprite(md.sprite_index, ground)
                    self.save_monster_attack_sprite(md.sprite_index, attack)
                    # update shadow size
                    md.shadow_size = ShadowSize(shadow_size_id).value  # type: ignore
                    # update sprconf.json
                    FileType.SPRCONF.update(sprconf, pmd2_sprite)
        except Exception:
            traceback_str = ''.join(traceback.format_exception(*sys.exc_info()))
            self._debugs.append((f'{pokedex_number:04}', poke_name, form_id, form_name, traceback_str))

        self.current += 1
        status.step(f"Downloading portraits and sprites... {self.current}/{self.total}")

    def save_monster_monster_sprite(self, id: int, data: WanFile):
        wdata = FileType.WAN.CHARA.serialize(data)
        xdata = FileType.PKDPX.serialize(FileType.PKDPX.compress(wdata))
        if id == len(self.monster_bin):
            self.monster_bin.append(xdata)
        else:
            self.monster_bin[id] = xdata

    def save_monster_ground_sprite(self, id: int, data: WanFile):
        wdata = FileType.WAN.CHARA.serialize(data)
        if id == len(self.monster_ground_bin):
            self.monster_ground_bin.append(wdata)
        else:
            self.monster_ground_bin[id] = wdata

    def save_monster_attack_sprite(self, id: int, data: WanFile):
        wdata = FileType.WAN.CHARA.serialize(data)
        xdata = FileType.PKDPX.serialize(FileType.PKDPX.compress(wdata))
        if id == len(self.monster_attack_bin):
            self.monster_attack_bin.append(xdata)
        else:
            self.monster_attack_bin[id] = xdata
