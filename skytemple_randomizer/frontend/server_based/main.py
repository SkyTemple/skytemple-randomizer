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
from typing import Callable

from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_files.common.types.file_types import FileType
from skytemple_randomizer.frontend.common_web.abstract import AbstractWebHandler, get_base_tornado_config
from tornado.web import Application
from tornado import websocket
import asyncio
import os
PORT = os.getenv('PORT', 44235)


class WebserverFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        pass  # todo


class RuntimeStorage:
    pass


class ServerBasedWebHandler(AbstractWebHandler):
    def get_additional_scripts(self):
        return []


class WebsocketHandler(websocket.WebSocketHandler):
    client_data = {}

    def check_origin(self, origin):
        return True

    def open(self):
        pass

    def on_close(self):
        pass

    async def on_message(self, message):
        pass


config, routes = get_base_tornado_config(ServerBasedWebHandler)
routes += [
    (r'/__ws', WebsocketHandler),
]
app = Application(routes, **config)
app.listen(PORT)
asyncio.get_event_loop().run_forever()
