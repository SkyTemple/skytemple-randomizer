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
import inspect
import os
from random import Random

_DEBUG_FILE_PATH = os.environ.get("SKYTEMPLE_RANDOMIZER_DEBUG_DIR_RNG", "/tmp/rng_debug")
_COUNTER = 0


class DebugRandom(Random):
    def __init__(self, x=None):
        global _COUNTER
        super().__init__(x)
        os.makedirs(_DEBUG_FILE_PATH, exist_ok=True)
        self.file = open(os.path.join(_DEBUG_FILE_PATH, f"{x}-{_COUNTER}.txt"), "w")
        _COUNTER += 1

    def _debug(self, meth_name, meth, *args, **kwargs):
        retval = meth(*args, **kwargs)
        stack = inspect.currentframe()
        frame = stack.f_back.f_back  # type: ignore
        f_code = frame.f_code  # type: ignore
        print(
            f"{f_code.co_filename}:{frame.f_lineno}:: {meth_name}(*{args=}, **{kwargs=}) -> {retval}",  # type: ignore
            file=self.file,
        )
        return retval

    def weibullvariate(self, alpha, beta):
        return self._debug("weibullvariate", super().weibullvariate, alpha, beta)

    def paretovariate(self, alpha):
        return self._debug("paretovariate", super().paretovariate, alpha)

    def vonmisesvariate(self, mu, kappa):
        return self._debug("vonmisesvariate", super().vonmisesvariate, mu, kappa)

    def lognormvariate(self, mu, sigma):
        return self._debug("lognormvariate", super().lognormvariate, mu, sigma)

    def normalvariate(self, mu=0.0, sigma=1.0):
        return self._debug("normalvariate", super().normalvariate, mu, sigma)

    def gauss(self, mu=0.0, sigma=1.0):
        return self._debug("gauss", super().gauss, mu, sigma)

    def gammavariate(self, alpha, beta):
        return self._debug("gammavariate", super().gammavariate, alpha, beta)

    def expovariate(self, lambd=1.0):
        return self._debug("expovariate", super().expovariate, lambd)

    def betavariate(self, alpha, beta):
        return self._debug("betavariate", super().betavariate, alpha, beta)

    def binomialvariate(self, n=1, p=0.5):
        return self._debug("binomialvariate", super().binomialvariate, n, p)

    def triangular(self, low=0.0, high=1.0, mode=None):
        return self._debug("triangular", super().triangular, low, high, mode)

    def uniform(self, a, b):
        return self._debug("uniform", super().uniform, a, b)

    def sample(self, population, k, *, counts=None):
        return self._debug("sample", super().sample, population, k, counts=counts)

    def shuffle(self, x):
        self._debug("shuffle", super().shuffle, x)

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        return self._debug("choices", super().choices, population, weights, cum_weights=cum_weights, k=k)

    def choice(self, seq):
        return self._debug("choice", super().choice, seq)

    def randbytes(self, n):
        return self._debug("randbytes", super().randbytes, n)

    def randint(self, a, b):
        return self._debug("randint", super().randint, a, b)

    def randrange(self, start, stop=None, step=1):
        return self._debug("randrange", super().randrange, start, stop, step)

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass
