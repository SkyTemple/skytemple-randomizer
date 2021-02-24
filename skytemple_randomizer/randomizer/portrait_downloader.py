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
import io
import json
import sys
import traceback

import math
import urllib.request

from PIL import Image
from gi.repository import GLib
from ndspy.rom import NintendoDSRom

from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_binary_from_rom_ppmdu
from skytemple_files.data.md.model import NUM_ENTITIES, Gender
from skytemple_files.graphics.kao.model import KaoImage
from skytemple_files.graphics.kao.sprite_bot_sheet import SpriteBotSheet
from skytemple_files.hardcoded.personality_test_starters import HardcodedPersonalityTestStarters
from skytemple_files.list.actor.model import ActorListBin
from skytemple_files.patch.patches import Patcher
from skytemple_randomizer.config import Global, RandomizerConfig
from skytemple_randomizer.randomizer.abstract import AbstractRandomizer
from skytemple_randomizer.status import Status


class PortraitDownloader(AbstractRandomizer):
    def __init__(self, config: RandomizerConfig, rom: NintendoDSRom, static_data: Pmd2Data, seed: str):
        super().__init__(config, rom, static_data, seed)
        self._debugs = []

    def step_count(self) -> int:
        if self.config['improvements']['download_portraits']:
            return 4
        return 0

    def run(self, status: Status):
        if not self.config['improvements']['download_portraits']:
            return status.done()

        status.step("Apply 'ActorAndLevelLoader' patch...")
        patcher = Patcher(self.rom, self.static_data)
        if not patcher.is_applied('ActorAndLevelLoader'):
            patcher.apply('ActorAndLevelLoader')

        overlay13 = get_binary_from_rom_ppmdu(self.rom, self.static_data.binaries['overlay/overlay_0013.bin'])
        actor_list: ActorListBin = FileType.SIR0.unwrap_obj(
            FileType.SIR0.deserialize(self.rom.getFileByName('BALANCE/actor_list.bin')), ActorListBin
        )
        starters = HardcodedPersonalityTestStarters.get_partner_md_ids(overlay13, self.static_data)
        partners = HardcodedPersonalityTestStarters.get_player_md_ids(overlay13, self.static_data)
        md = FileType.MD.deserialize(self.rom.getFileByName('BALANCE/monster.md'))

        with urllib.request.urlopen("http://sprites.pmdcollab.org/resources/pokemons.json") as url:
            config = json.loads(url.read().decode())

        kao = FileType.KAO.deserialize(self.rom.getFileByName('FONT/kaomado.kao'))

        status.step("Downloading portraits for NPCs...")
        for actor in actor_list.list:
            if actor.entid > 0:
                self._import_portrait(kao, config, actor.entid, md.entries[actor.entid])

        status.step("Downloading portraits for starters...")
        for starter in starters:
            self._import_portrait(kao, config, starter, md.entries[starter])

        status.step("Downloading portraits for partners...")
        for partner in partners:
            self._import_portrait(kao, config, partner, md.entries[partner])

        self.rom.setFileByName('FONT/kaomado.kao', FileType.KAO.serialize(kao))

        def add_rows():
            o = Global.main_builder.get_object('store_debug_portraits')
            o.clear()
            for row in self._debugs:
                o.append(row)

        GLib.idle_add(add_rows)

        status.done()

    def _import_portrait(self, kaos, config, mdidx, md):
        pokedex_number = md.national_pokedex_number
        form_id = ''
        poke_name = ''
        form_name = ''
        try:
            forms_to_try = ['0000']
            if md.gender == Gender.FEMALE:
                forms_to_try.insert(0, '0000f')
            if mdidx == 279:  # Celebi Shiny
                forms_to_try.insert(0, '0000s')
            if f'{pokedex_number:04}' in config and '0000' in config[f'{pokedex_number:04}']['forms']:
                filename = None
                for form in forms_to_try:
                    if form in config[f'{pokedex_number:04}']['forms']:
                        filename = config[f'{pokedex_number:04}']['forms'][form]['filename']
                        form_id = form
                        break
                if filename is None:
                    return
                poke_name = config[f'{pokedex_number:04}']['name']
                form_name = config[f'{pokedex_number:04}']['forms'][form_id]['name']
                url = f'http://sprites.pmdcollab.org/resources/portraits/{filename}'
                with urllib.request.urlopen(url) as download:
                    for subindex, image in SpriteBotSheet.load(io.BytesIO(download.read()), self._get_portrait_name):
                        kao = kaos.get(mdidx - 1, subindex)
                        if kao:
                            # Replace
                            kao.set(image)
                        else:
                            # New
                            kaos.set(mdidx - 1, subindex, KaoImage.new(image))
                self._debugs.append([f'{pokedex_number:04}', poke_name, form_id, form_name, '✓'])
        except BaseException:
            traceback_str = ''.join(traceback.format_exception(*sys.exc_info()))
            self._debugs.append([f'{pokedex_number:04}', poke_name, form_id, form_name, traceback_str])


    def _get_portrait_name(self, subindex):
        portrait_name = self.static_data.script_data.face_names__by_id[
            math.floor(subindex / 2)
        ].name.replace('-', '_')
        portrait_name = f'{subindex}: {portrait_name}'
        if subindex % 2 != 0:
            portrait_name += ' (flip)'
        return portrait_name
