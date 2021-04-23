#!/usr/bin/env python
""" Level set wrapper providing convenience methods.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""
import os
import attr
import time
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
class ReachableSetWrapper:
    """ Encapsulates convenience methods to access reachable sets.

        Note:
            Initialise using previously exported `*.levelset` using
            the `from_memory` argument or parse a label and path to
            initialise from a `*.mat` file.

            ReachableSetData provides access to grid indices and their
            respective states using Grid, value function values or sublevel sets.

            On initialisation for each discretised time step a
            ReachableSetData entry is added to the `sets` attribute.

    """
    ## Initialisation arguments
    label = attr.ib(type=str)
    ## 1. (optional) Retrieve from memory using path to *.levelset binary
    from_memory = attr.ib(default=None, type=typing.Optional[str])
    ## 2. (optional) Initialisation from raw data using path to *.mat file
    path = attr.ib(default=None, type=typing.Optional[str])

    grid = attr.ib(default=None, type=typing.Optional[pylevel.data.Grid])
    time = attr.ib(default=None, type=typing.Optional[list])

    ## Sets dictionary with (key,value) of type (time,LevelSetDict)
    ## -> The LevelSetDict consists of
    # keys: (grid_indices,states,value_function,ReachableSetData)
    # type: (list,numpy.array,dict,GridData)
    sets = attr.ib(
            default=None,
            type=typing.Optional[typing.Dict[float, pylevel.data.ReachableSetData]])
    value_function = attr.ib(
            default=None,
            type=typing.Optional[typing.Dict[tuple, numpy.ndarray]])

    ## Global state set dictionary with (key,value) of type (state,None)
    states = attr.ib(default=None, type=typing.Optional[dict])

    show_config = attr.ib(default=False, type=bool)
    ## Export if load_from memory is not provided or fails
    initialise_once = attr.ib(default=True, type=bool)
    debug_is_enabled = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        if self.from_memory is None:
            self.from_memory = os.getcwd()

        ## Attempt to load from memory
        if self.initialise_once:
            try:
                self._load_from_memory()
                return
            except Exception as e:
                self.debug("Initialise from memory failed: {}".format(e))
                raise RuntimeError()
        ## If no previous data is provided initialise first
        self._initialise_from_raw_data()
        self.export()

    def _initialise_from_raw_data(self):
        self.debug("Initialise from: {}".format(self.path))
        ## Initialise loader (without storing raw data reference)
        data = loadmat(self.path)
        # Grid with ds dimensional array and Nx1, Nx2, Nx3, Nxn entries
        self.grid = data['g']
        # States
        self.states = dict()

        kt = None
        for key in data.keys():
            if 'time' in key.split("_"):
                kt = key
            elif 'data' in key.split("_"):
                kd = key

        # Time as list from 0 to tf
        self.time = data[kt].tolist()[0]
        # Value function with dx1, dx2, ..., dxn, t
        self.value_function = data[kd]

        # Helper to access grid indices or states and their discretisation
        self.grid = pylevel.data.Grid(
                grid=self.grid,
                show_config=self.show_config,
                debug_is_enabled=self.debug_is_enabled)
        self._initialise_sets()

    def _load_from_memory(self):
        """ Fetch from previously exported (memorised) configuration. """
        path = self.from_memory
        identifier = self.label + ".levelset"
        filepath = '/'.join([path, identifier])
        file_size = os.path.getsize(filepath)
        print('Size: ', file_size)

        self.debug('Import from filepath:', filepath)
        with open(filepath, "rb") as f:
            data_loaded = pickle.load(f)
        self.__dict__.update(**data_loaded)

    def debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("LevelSetWrapper: ", *args)

    def export(self, path : str = None):
        """ Export current class as pickle dump. """
        path = os.getcwd() if path is None else path
        identifier = self.label + ".levelset"
        filepath = '/'.join([path,identifier])

        self.debug('Export to filepath:', filepath)

        with open(filepath, "wb") as f:
            pickle.dump(self.__dict__, f)

        self.debug("Exported levelset: {} with identifier: {}".format(
            self.label, identifier))

    def _initialise_sets(self):
        """ Iterate over discretised time and initialise corresponding ttr. """
        self.sets = dict()
        grid = self.grid
        for t_idx, _ in enumerate(self.time):
            stamp = time.time()
            self.debug('Initialising set {} of {}'.format(t_idx, len(self.time)))
            level_set_dict = dict()
            grid_indices = dict()

            ## ReachableSetData provides parser functionality
            # to access sets, values and grid_indices
            reachable_set = pylevel.data.ReachableSetData(
                    grid=grid,
                    data=self.value_function[:, :, :, :, t_idx])
            indices = reachable_set.sublevel_indices(level=0.0)

            ## Collect states from grid indices and conveniently create dict
            states = list()
            value_function_dict = dict()
            for index in indices:
                grid_indices[index] = True
                state = grid.state(index)
                states.append(state)
                value_function_dict[tuple(state)] = reachable_set.value_function(state)

            ## Asume numpy array
            states = numpy.array(states)

            for state in states:
                ## Create tuple
                t = tuple(state)
                self.states[t] = None

            states = numpy.array(states)

            ## Dict with indice key and boolean to define membership
            level_set_dict['grid_indices'] = grid_indices
            ## States numpy array
            level_set_dict['states'] = states
            ## Dict with state key and value function value entry
            level_set_dict['value_function'] = value_function_dict
            level_set_dict['reachable_set'] = reachable_set

            ## Convexify states
            hull = ConvexHull(states)
            vertices = [hull.points[[i], :].reshape(-1, 1) for i in hull.vertices]
            vertices = numpy.squeeze(numpy.array(vertices))
            level_set_dict['states_convexified'] = vertices

            ## Update global set dictionary
            self.sets[t_idx] = level_set_dict
            self.debug('--> Initialised in {}s'.format(time.time() - stamp))
        self.debug('All sets initialised.')

    def reach_at_t(self,
            t : float,
            convexified=False):
        """ Return level set set at time t or closest discretised index. """
        ts = numpy.array(self.time)
        t_idx = numpy.abs(ts - t).argmin()

        state_key = "states_convexified" if convexified else "states"

        return self.sets[int(numpy.asscalar(t_idx))][state_key]

    def reach_at_ttr(self,
            state : numpy.ndarray,
            convexified : bool=False):
        """ Return minimial time to reach set and its discretised time. """


        closest_grid_index = self.grid.index(state)

        state_key = "states_convexified" if convexified else "states"

        for time_index, set_dictionary in self.sets.items():
            grid_indices = set_dictionary['grid_indices']

            if closest_grid_index in grid_indices:
                return set_dictionary[state_key], self.time[time_index]

        self.debug('Failed to find index in any set: Unreachable')
        raise pylevel.error.StateNotReachableError()

    def is_member(self, state: numpy.ndarray):
        """ Return if state is member with level set agnostic membership. """
        return state in self.states

    def is_not_member(self, state: numpy.ndarray):
        """ Return if state is member with level set agnostic membership. """
        return not state in self.states

