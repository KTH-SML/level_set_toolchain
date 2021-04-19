#!/usr/bin/env python
""" Level set wrapper providing convenience methods.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""

import attr
import numpy
import typing
import pickle

from scipy.io import loadmat
from scipy.spatial import ConvexHull


import pylevel


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"


@attr.s
class LevelSetWrapper:
    """ Encapsulates level set functions.

        Note:
            Either initialise using previously exported `*.levelset` o

            - GridData is a parser to provide access to grid indices and their
            respective states, value function values or sublevel sets.

    """
    ## Initialisation arguments
    label = attr.ib(type=str)
    ## 1. (optional) Retrieve from memory using path to *.levelset binary
    from_memory = attr.ib(default=None, type=typing.Optional[str])
    ## 2. (optional) Initialisation from raw data using path to *.mat file
    path = attr.ib(default=None, type=typing.Optional[str])

    grid_helper = attr.ib(default=None, type=typing.Optional[pylevel.grid.Grid])
    grid = attr.ib(default=None, type=typing.Optional[dict])
    time = attr.ib(default=None, type=typing.Optional[list])

    ## Sets dictionary with (key,value) of type (time,LevelSetDict)
    ## -> The LevelSetDict consists of
    # keys: (grid_indices,states,value_function,parser)
    # type: (list,numpy.array,dict,GridData)
    sets = attr.ib(default=None, type=typing.Optional[dict])
    value_function = attr.ib(default=None, type=typing.Optional[dict])

    ## Global state set dictionary with (key,value) of type (state,None)
    states = attr.ib(default=None, type=typing.Optional[dict])

    _show_config = attr.ib(default=False, type=bool)
    _debug_is_enabled = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        if self.from_memory is not None:
            self._load_from_memory()
            return

        ## If no previous data is provided initialise first
        self._initialise_from_raw_data()

    def is_member(self, state: numpy.ndarray):
        """ Return if state is member with level set agnostic membership. """
        return state in self.states

    def _initialise_from_raw_data(self):
        ## Initialise loader (without storing raw data reference)
        data = loadmat(self.path)
        # Grid with ds dimensional array and Nx1, Nx2, Nx3, Nxn entries
        self.grid = data['g']
        # States
        self.states = dict()
        # Time as list from 0 to tf
        self.time = data['BRS_time'].tolist()[0]
        # Value function with dx1, dx2, ..., dxn, t
        self.value_function = data['BRS_data']
        # Helper to access grid indices or states and their discretisation
        self.grid_helper = pylevel.grid.Grid(
                grid=self.grid,
                show_config=self._show_config)
        self._initialise_sets()

    def _load_from_memory(self):
        """ Fetch from previously exported (memorised) configuration. """
        with open(self.from_memory, "rb") as f:
            data_loaded = pickle.load(f)
        self.__dict__(**data_loaded)

    def _debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self._debug_is_enabled:
            print("LevelSetWrapper: ", *args)

    def export(self, identifier, path):
        """ Export  """
        with open('/'.join([path,identifier]), "wb") as f:
            pickle.dump(self.__dict__, f)
        self._debug("Exported levelset: {} with identifier: {}".format(
            self.label, identifier))

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

            ## Asume numpy array
            states = numpy.array(states)

            d = dict()
            ## Append states to global (whole time interval) state set
            self.states.update(
                    dict([
                            (tuple(state.reshape((-1, 1)).tolist()), True)
                            for state in states
                        ]))

            ## Dict with indice key and boolean to define membership
            level_set_dict['grid_indices'] = grid_indices
            ## States numpy array
            level_set_dict['states'] = states
            ## Dict with state key and value function value entry
            level_set_dict['value_function'] = value_function_dict
            level_set_dict['parser'] = parser

            ## Convexify states
            hull = ConvexHull(states)
            vertices = [hull.points[[i], :].reshape(-1,1) for i in hull.vertices]
            vertices = numpy.squeeze(numpy.array(vertices))
            level_set_dict['states_convexified'] = vertices

            ## Update global set dictionary
            self.sets[t_idx] = level_set_dict
        print('All sets initialised.')

    def get_reachable_set_at_time(self, t, convexified=False):
        """ Return level set set at time t or closest discretised index. """
        ts = numpy.array(self.time)
        t_idx = numpy.abs(ts - t).argmin()

        state_key = "states_convexified" if convexified else "states"

        return self.sets[int(numpy.asscalar(t_idx))][state_key]

    def get_reachable_set(self, state : list, convexified=False):
        """ Return reachable states and its set index.


            Note:
                This is the minimal time to reach levelset.

        """


        closest_grid_index = self.grid_helper.get_index_of_rounded_state(state)

        state_key = "states_convexified" if convexified else "states"

        for time_index, set_dictionary in self.sets.items():
            grid_indices = set_dictionary['grid_indices']

            if closest_grid_index in grid_indices:
                return set_dictionary[state_key], self.time[time_index]

        print('Failed to find index in any set: Unreachable')
        raise RuntimeError()

