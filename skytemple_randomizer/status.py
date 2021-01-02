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
from threading import Lock


class Status:
    """A threadsafe class for signaling status updates"""
    DONE_SPECIAL_STR = '<<<<<<< DONE'

    def __init__(self):
        self.counter = 0
        self.lock = Lock()
        self.subscribers = []

    def step(self, descr: str):
        with self.lock:
            self.counter += 1
            for subscriber in self.subscribers:
                subscriber(self.counter, descr)

    def done(self):
        self.step(self.DONE_SPECIAL_STR)
        with self.lock:
            self.subscribers = []

    def subscribe(self, subscribe_fn):
        with self.lock:
            self.subscribers.append(subscribe_fn)
