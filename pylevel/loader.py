#!/usr/bin/env python

import os


import attr
import typing
from scipy.io import loadmat


import pylevel


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"


@attr.s
class Loader:
    dataset = attr.ib(default=None, type=typing.Optional[pylevel.datasets.LevelSet])
    path = attr.ib(default=None, type=typing.Optional[str])

    data = attr.ib(default=None, type=typing.Optional[dict])

    def __attrs_post_init__(self):
        if self.path is None:
            self.path = os.path.dirname(os.path.abspath(__file__))
        self._load_data()

    def _load_data(self):
        path = pylevel.datasets.path[self.dataset]
        self.data = loadmat(path)


