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
    ## TODO: LEGACY dataset
    dataset = attr.ib(default=None, type=typing.Optional[pylevel.datasets.LevelSet])
    ## Level set type to identify state set
    level_set = attr.ib(default=None, type=typing.Optional[pylevel.datasets.LevelSet])
    path = attr.ib(default=None, type=typing.Optional[str])

    data = attr.ib(default=None, type=typing.Optional[dict])

    ## Custom type to path dictionary
    set_types = attr.ib(default=None, type=typing.Optional[
        typing.TypedDict[
            pylevel.datasets.LevelSet]])

    def __attrs_post_init__(self):
        ## TODO: LEGACY mode using dataset as target specification
        if self.level_set is None:
            self.level_set == self.dataset
        self._load_data()

    def _load_data(self):
        if set_types is None:
            path = pylevel.datasets.path[self.level_set]
        else:
            path = set_types[self.level_set]
        self.data = loadmat(path)


