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
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
import base64
import json
import random
import traceback
from asyncio import sleep
from datetime import datetime
from functools import partial
from typing import Callable, Dict, Any

import tornado.web
from ndspy.rom import NintendoDSRom

from skytemple_randomizer.config import ConfigFileLoader, get_effective_seed
from skytemple_randomizer.frontend.abstract import AbstractFrontend
from skytemple_randomizer.frontend.common_web.abstract import AbstractWebHandler, get_base_tornado_config
from tornado.web import Application
from tornado import websocket, httputil
import asyncio
import os

from skytemple_randomizer.randomizer_thread import RandomizerThread
from skytemple_randomizer.status import Status

PORT = int(os.getenv('PORT', 44235))
LOOP = asyncio.get_event_loop()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WebserverFrontend(AbstractFrontend):
    def idle_add(self, fn: Callable):
        self.run_on_main_thread(fn)

    @classmethod
    def run_on_main_thread(cls, fn: Callable):
        LOOP.call_soon_threadsafe(fn)

    @classmethod
    def run_timeout(cls, x, fn: Callable):
        """Runs fn after x sec. If it returns True, it will be run again after x sec."""
        LOOP.call_soon_threadsafe(lambda: asyncio.ensure_future(cls._run_timeout_impl(x, fn), loop=LOOP))

    @classmethod
    async def _run_timeout_impl(cls, x, fn: Callable):
        logger.debug("Run Timeout called")
        await sleep(x)
        while fn():
            await sleep(x)
        logger.debug("Run Timeout over")


# noinspection PyAbstractClass
class ServerBasedWebHandler(AbstractWebHandler):
    def get_additional_scripts(self):
        return ['/server/randomize.js']


class RomStorage:
    # we are never cleaning this. fine for Android, not fine for a REAL web server based approach!
    roms: Dict[Any, NintendoDSRom] = {}


class UploadHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        logger.debug(f'{self.request.remote_ip}: Upload request.')
        RomStorage.roms[self.request.remote_ip] = NintendoDSRom(self.request.body)
        self.write("ok.")
        await self.flush()


class DownloadHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        if self.request.remote_ip in RomStorage.roms:
            logger.debug(f'{self.request.remote_ip}: Download request.')
            f = RomStorage.roms[self.request.remote_ip].save()
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header("Content-Transfer-Encoding", "Binary")
            self.set_header('Content-Disposition', f'attachment; filename=randomizedEOS_{datetime.now().strftime("%d-%m-%y-%I%M%S")}.nds')
            self.set_header('Content-Length', str(len(f)))
            self.write(f)
            await self.flush()
        else:
            logger.warning(f'{self.request.remote_ip}: Download request - not found.')
            self.set_status(404, 'Not Found')
            self.write("ROM not found.")
            await self.flush()


# noinspection PyAbstractClass
class WebsocketHandler(websocket.WebSocketHandler):
    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs):
        super().__init__(application, request, **kwargs)
        self.randomization_is_running = False
        self.rom = None
        self.static_data = None
        self.config = None

    def check_origin(self, origin):
        return True

    def open(self):
        logger.debug(f'{self.request.remote_ip}: Connected.')

    def on_close(self):
        logger.debug(f'{self.request.remote_ip}: Disconnected.')

    async def on_message(self, message):
        decoded_message = json.loads(message)
        logger.debug(f'{self.request.remote_ip}: Sent msg.')
        try:
            if not self.randomization_is_running:
                if decoded_message['action'] == 'start':
                    logger.info(f'{self.request.remote_ip}: Sent start request.')
                    self.randomization_is_running = True
                    config = ConfigFileLoader.load_from_dict(decoded_message['config'])
                    rom = RomStorage.roms[self.request.remote_ip]
                    seed = get_effective_seed(config['seed'])
                    random.seed(seed)
                    status = Status()

                    def update_fn(progress, desc):
                        logger.debug(f'{self.request.remote_ip}: {round((progress - 1 / randomizer.total_steps * 100))}: {desc}')
                        if desc == Status.DONE_SPECIAL_STR:
                            self.write_message(json.dumps(
                                {'status': 'progress', 'step': progress - 1, 'totalSteps': randomizer.total_steps,
                                 'message': "Randomizing complete!", 'seed': seed}))
                        else:
                            self.write_message(json.dumps(
                                {'status': 'progress', 'step': progress - 1, 'totalSteps': randomizer.total_steps,
                                 'message': desc, 'seed': seed}))

                    def check_done():
                        if not randomizer.is_done():
                            return True
                        logger.debug(f'{self.request.remote_ip}: Check done!')
                        if randomizer.error:
                            traceback_str = ''.join(traceback.format_exception(*randomizer.error))
                            logger.error(f'{self.request.remote_ip}: ERROR: {traceback_str}')
                            self.write_message(json.dumps(
                                {'status': 'error',
                                 'message': f"Error: {traceback_str}", 'seed': seed}))
                        else:
                            logger.info(f'{self.request.remote_ip}: DONE!')
                            self.write_message(json.dumps(
                                {'status': 'done', 'step': randomizer.total_steps, 'totalSteps': randomizer.total_steps,
                                 'message': "Randomization complete!", 'seed': seed}))
                        return False

                    status.subscribe(lambda a, b: WebserverFrontend.run_on_main_thread(partial(update_fn, a, b)))
                    randomizer = RandomizerThread(status, rom, config, seed, WebserverFrontend())

                    WebserverFrontend.run_timeout(0.1, check_done)

                    randomizer.start()
        except BaseException as ex:
            self.randomization_is_running = False
            tb = traceback.format_exc()
            print(tb)
            await self.write_message(json.dumps({'status': 'error', 'message': f"Fatal error: {ex}\n{tb}"}))


sconfig, routes = get_base_tornado_config(ServerBasedWebHandler)
routes += [
    (r'/__ws', WebsocketHandler),
    (r'/server/(.*)', tornado.web.StaticFileHandler,
     {'path': os.path.join(os.path.dirname(__file__), 'view')}),
    (r'/upload', UploadHandler),
    (r'/download', DownloadHandler)
]
app = Application(routes, **sconfig)
app.listen(PORT, max_buffer_size=314572800)
LOOP.run_forever()
