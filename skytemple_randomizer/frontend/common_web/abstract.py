#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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
import os
import sys

import tornado.web

from skytemple_files.common.ppmdu_config.xml_reader import Pmd2XmlReader
from skytemple_files.data.md.model import Ability
from skytemple_files.dungeon_data.mappa_bin.item_list import MAX_ITEM_ID
from skytemple_randomizer.config import data_dir, RandomizerConfig, version
from abc import ABC, abstractmethod

from skytemple_randomizer.lists import MONSTERS, MOVES


class ConfigDocDumper:
    """Returns the strings of the *Doc classes as dict."""
    def apply(self):
        return self._handle(type(None), RandomizerConfig)

    def _handle(self, parent_typ: type, typ: type, field_name=None, field_name_short=None):
        if hasattr(typ, '__bases__') and dict in typ.__bases__ and len(typ.__annotations__) > 0:
            d = {}
            for field, field_type in typ.__annotations__.items():
                field_full = field
                if field_name is not None:
                    field_full = field_name + '_' + field
                d[field] = self._handle(typ, field_type, field_full, field)
            return d
        if hasattr(parent_typ, '__name__'):
            current_module = sys.modules['skytemple_randomizer.config']
            if parent_typ.__name__ + 'Doc' in current_module.__dict__:
                cls = current_module.__dict__[parent_typ.__name__ + 'Doc']
                if field_name_short in cls.__dict__:
                    return '\n'.join([line.strip() for line in cls.__dict__[field_name_short].splitlines()])


class AbstractWebHandler(tornado.web.RequestHandler, ABC):
    async def get(self, *args, **kwargs):
        await self.render(
            'view.html.jinja2',  # Note: Tornado does not actually use jinja2! But it's close.
            additional_scripts=self.get_additional_scripts(),
            default_randomizer_config=self.get_default_config(),
            help_texts=json.dumps(self.get_help_texts()),
            version=version(),
            dungeon_names=self.get_dungeon_names(),
            ability_names=self.get_ability_names(),
            item_names=self.get_item_names(),
            move_names=self.get_move_names(),
            monster_names=self.get_monster_names()
        )

    def get_default_config(self):
        with open(os.path.join(data_dir(), 'default.json')) as f:
            return f.read()

    def get_help_texts(self):
        return ConfigDocDumper().apply()

    def get_dungeon_names(self):
        static_data = Pmd2XmlReader.load_default('EoS_EU')  # version doesn't really matter for this
        return {dungeon.id: dungeon.name for dungeon in static_data.dungeon_data.dungeons}

    def get_monster_names(self):
        return MONSTERS

    def get_item_names(self):
        static_data = Pmd2XmlReader.load_default('EoS_EU')  # version doesn't really matter for this
        return {item.id: item.name for item in static_data.dungeon_data.items if item.id <= MAX_ITEM_ID}

    def get_move_names(self):
        return MOVES

    def get_ability_names(self):
        return {ability.value: ability.print_name for ability in Ability if ability.value != 0xFF}

    @abstractmethod
    def get_additional_scripts(self):
        pass


def get_base_tornado_config(handler_cls, handler_arguments=None):
    DEFAULT_APP_CONFIG = {
        'template_path': os.path.join(os.path.dirname(__file__), 'view'),
        'static_path': os.path.join(os.path.dirname(__file__), 'view', 'static'),
    }

    DEFAULT_ROUTES = [
        (r"/", handler_cls, handler_arguments),
        (r'/favicon.ico', tornado.web.StaticFileHandler,
         {'path': os.path.join(DEFAULT_APP_CONFIG['static_path'], 'favicon.ico')}),
        (r'/modules/(.*)', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), 'node_modules')}),
        (r'/data/(.*)', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), '..', '..', 'data')}),
    ]

    return DEFAULT_APP_CONFIG, DEFAULT_ROUTES
