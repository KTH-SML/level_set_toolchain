#!/usr/bin/env python

import attr
import numpy
import typing
import pylevel


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"


@attr.s
class LevelSetWrapper(pylevel.loader.Loader):
    grid_helper = attr.ib(default=None, type=typing.Optional[pylevel.grid.Grid])

    grid = attr.ib(default=None, type=typing.Optional[dict])
    time = attr.ib(default=None, type=typing.Optional[dict])
    sets = attr.ib(default=None, type=typing.Optional[list])
    value_function = attr.ib(default=None, type=typing.Optional[dict])

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # TODO: document shape
        self.grid = self.data['g']
        # TODO: document shape
        self.time = self.data['BRS_time'].tolist()[0]
        # Shape: 1 value_function per timestep
        self.value_function = self.data['BRS_data']
        # TODO: GridData uses Grid already?
        self.grid_helper = pylevel.grid.Grid(self.grid)
        self._initialise_sets()

    def _initialise_sets(self):
        self.sets = list()
        for t_idx,_ in enumerate(self.time):
            BRS = pylevel.grid.GridData(self.grid, self.value_function[:, :, :, :, t_idx])
            self.sets.append(BRS.sublevel_set_idx(level=0.0))

    def get_reachable_set_at_time(self, t):
        ts = numpy.array(self.time)
        t_idx = numpy.abs(ts - t).argmin()
        return numpy.array(self.sets[int(numpy.asscalar(t_idx))])

    def get_reachable_set(self, state : list):
        """ Return reachable states and its set index

            Note:
                Return (None,None) if unsuccessful

            Todo:
                - Currently does not support numpy due to round
        """
        for set_idx, grid_coordinates in enumerate(self.sets):
            grid_coordinate = self.grid_helper.get_idx(state)
            if grid_coordinate in grid_coordinates:
                return numpy.array(grid_coordinates), set_idx
        print('Failed to find coordinate in any set: Unreachable')
        raise RuntimeError()

