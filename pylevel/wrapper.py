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
    """ Encapsulates level set functions.

        Note:
            Requires dataset as argument see `pylevel.loader.Loader`.

            - GridData is a parser to provide access to grid indices and their
            respective states, value function values or sublevel sets.

    """
    grid_helper = attr.ib(default=None, type=typing.Optional[pylevel.grid.Grid])
    grid = attr.ib(default=None, type=typing.Optional[dict])
    time = attr.ib(default=None, type=typing.Optional[list])

    ## Levelsets as dict with grid_indices and values
    ## Dict with time key and dict entry
    ## The dict entry has grid_indices, states, value_function and parser
    ## with list, numpy.array, dict, and GridData type
    sets = attr.ib(default=None, type=typing.Optional[list])
    value_function = attr.ib(default=None, type=typing.Optional[dict])

    show_config = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        # Grid with ds dimensional array and Nx1, Nx2, Nx3, Nxn entries
        self.grid = self.data['g']
        # Time as list from 0 to tf
        self.time = self.data['BRS_time'].tolist()[0]
        # Value function with dx1, dx2, ..., dxn, t
        self.value_function = self.data['BRS_data']
        # Helper to access grid indices or states and their discretisation
        self.grid_helper = pylevel.grid.Grid(
                grid=self.grid,
                show_config=self.show_config)
        self._initialise_sets()

    def _initialise_sets(self):
        self.sets = dict()
        for t_idx,_ in enumerate(self.time):
            level_set_dict = dict()
            grid_indices = dict()

            # GridData provides parser functionality to access sets, values and grid_indices
            parser = pylevel.grid.GridData(
                    grid=self.grid,
                    data=self.value_function[:, :, :, :, t_idx])
            indices = parser.sublevel_set_idx(level=0.0)
            for entry in indices:
                grid_indices[entry] = True

            # Collect states from grid indices and conveniently create dict
            states = list()
            value_function_dict = dict()
            for index in grid_indices:
                states.append(parser.get_state_of_index(index))
                value_function_dict[tuple(states[-1])] = parser.data[index]
            states = numpy.array(states)

            ## Dict with indice key and boolean to define membership
            level_set_dict['grid_indices'] = grid_indices
            ## States numpy array
            level_set_dict['states'] = states
            ## Dict with state key and value function value entry
            level_set_dict['value_function'] = value_function_dict
            level_set_dict['parser'] = parser

            self.sets[t_idx] = level_set_dict
        print('All sets initialised.')

    def get_reachable_set_at_time(self, t):
        ts = numpy.array(self.time)
        t_idx = numpy.abs(ts - t).argmin()

        return self.sets[int(numpy.asscalar(t_idx))]['states']

    def get_reachable_set(self, state : list):
        """ Return reachable states and its set index

            Todo:
                - Currently does not support numpy due to round in
                get_index_of_rounded_state
        """

        closest_grid_index = self.grid_helper.get_index_of_rounded_state(state)
        closest_state = self.grid_helper.get_state_of_index(closest_grid_index)

        for time_index, set_dictionary in self.sets.items():
            grid_indices = set_dictionary['grid_indices']
            parser = set_dictionary['parser']

            if closest_grid_index in grid_indices:
                return set_dictionary['states'], self.time[time_index]

        print('Failed to find index in any set: Unreachable')
        raise RuntimeError()

