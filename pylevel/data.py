#!/usr/bin/env python
""" Grid module providing objects to interface with imported .mat file.

    Grid module containing classes that work with saved MATLAB outputs
    of the Level Set Toolbox and helperOC.
    Much of the work is ported from helperOC into Python,
    with some additional convenience features added in.

"""
import attr
import enum
import math
import h5py
import numpy
import typing
import dask.array
import hdf5storage
from scipy.interpolate import interpn

import pylevel


__license__ = "MIT"
__author__ = "Frank Jiang, Philipp Rothenhäusler"
__maintainer__ = "Frank Jiang"
__email__ = "frankji@kth.se "
__status__ = "Development"


class InterpolationMethod(enum.IntEnum):
    """ Enumeration identifying interpolation methods for state lookup. """
    Undefined = 0
    Linear = 1


@attr.s
class Grid:
    """ Grid component for interfacing .mat level sets. """
    ## HDF5 data handle for optimised access coordination
    data_handle=attr.ib(type=str)
    ## Filepath to hdf data
    data_path=attr.ib(type=str)
    ## Discretisation grid
    grid = attr.ib(default=None, type=typing.Optional[numpy.array])
    ## Dimension of state space
    dim = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Grid discretisation step along each dimension
    dx = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Minimum state value on grid start
    x_min = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Maximum state value on grid end
    x_max = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Maximum state value on grid end
    index_max = attr.ib(default=None, type=typing.Optional[int])
    ## Count of grid elements along each dimension
    N = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Grid discretisation step along each dimension
    N_data = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Boundary condition to specify behaviour
    boundary = attr.ib(default=None, type=typing.Optional[typing.List])
    ## Convenience variable ds dimensional
    vs = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Enable debugging
    debug_is_enabled = attr.ib(default=False, type=bool)
    ## Show configuration
    show_config = attr.ib(default=True, type=bool)

    ## LEGACY
    ## Unused - kept as reference: to be documented
    # self.xs = g[7].reshape((self.dim,)).tolist()
    ## Unused - kept as reference: to be documented
    # self.boundaryData = g[8].reshape((self.dim,)).tolist()
    ## Unused - kept as reference: same info as N
    # self.shape = tuple(g[10][0].tolist())

    def __attrs_post_init__(self):
        """ Initialise from MATLAB *.mat file. """
        self.debug('Grid initialising')
        self.debug('Received data handle: ', self.data_handle)

        self.debug('Initialising grid...')
        self.grid = self.data_handle['/data/grid']
        self.dim = self._initialise_field('dim').astype(int)
        self.dx = self._initialise_field('dx')
        self.x_min = self._initialise_field('min')
        self.x_max = self._initialise_field('max')

        ## Maximum index along each dimension
        self.index_min = numpy.zeros(self.dx.shape).flatten()
        ## TODO: Verify maximum index as len - 1
        self.index_max = numpy.divide(self.x_max - self.x_min, self.dx).astype(int) 
        self.N = self._initialise_field('N').astype(int)

        self.N_data = numpy.prod(self.N)

        ## TODO: Decide and time complexity that is bearable
        # for single desktop workstation
        if self.N_data > 20000:
            print('WARNING: Complexity is very high ({})'.format(self.N_data))

        ## Initialise using loadmat to parse MATLAB cell array
        self.boundary = hdf5storage.read(path='/data/grid/bdry/', filename=self.data_path)

        ## Initialise using loadmat to parse MATLAB cell array
        self.vs = hdf5storage.read(path='/data/grid/vs/', filename=self.data_path)

        if self.show_config:
            self.print_config()

    def _index_in_grid(self, index):
        """ Return true if all elements satisfy grid resolution. """
        #print('Compare with: \t {} \n min: \t{}\n max: \t {}'.format(
        #        index, self.index_min, self.index_max))
        #print('self.x_max:', self.x_max)
        #print('self.dx:', self.dx)
        return (self.index_min <= index).all() and (index <= self.index_max).all()

    def index_neighbours(self, index, axes : typing.List[int], return_offset=False):
        """ Return valid neighbours for specified axes.

            Note:
                Index should be one dimensional.

        """

        ## TODO: Drone specific implementation (Use axis to generate pairing)
        # For each axis +1 and -1 each axis,
        # then for all extend with next axis, etc.
        ## Orthogonal neighbours
        if False:
            indices_offset = numpy.array([
                                 [-1, 0, 0, 0],
                                 [1, 0, 0, 0],
                                 [0, 0, -1, 0],
                                 [0, 0, 1, 0]])
        ## Diagonal and orthogonal neighbours
        indices_offset = numpy.array([
                             [-1, 0, 0, 0],
                             [1, 0, 0, 0],
                             [-1, 0, -1, 0],
                             [1, 0, -1, 0],
                             [-1, 0, 1, 0],
                             [1, 0, 1, 0],
                             [0, 0, -1, 0],
                             [0, 0, 1, 0]
                        ])

        indices = numpy.add(index, indices_offset)
        indices_mask = numpy.apply_along_axis(self._index_in_grid, arr=indices, axis=1)

        ## Test if any neighbours have been found
        if not indices_mask.any():
            raise IndexHasNoValidNeighboursError()

        if return_offset:
            return indices[indices_mask], indices_offset[indices_mask]
        return indices[indices_mask]

    def _initialise_field(self, field_name):
        """ Initialise dask array from hdf5 file. """
        return numpy.squeeze(dask.array.from_array(self.grid[field_name], chunks=1).compute())

    def print_config(self, x : typing.Optional[numpy.ndarray] = None):
        """ Visualise configuration and current state index. """

        print('Grid configuration:')
        print('Grid (min | max): ({} | {})'.format(self.x_min, self.x_max))
        print('Grid step size: ', self.dx[...])
        print('Grid index (min | max): ({} | {})'.format(self.index_min, self.index_max))

        print('Complexity:')
        print('--> Dimension:', self.dim[...])
        print('--> Datapoints: ', self.N_data[...])

    def _is_dimension_periodic(self, dim: None) ->  bool:
        """ Return if grid dimension is labeled periodic in MATLAB. """
        return "addGhostPeriodic" in self.boundary[dim][0][0][3][0][0][0][0]

    def debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("LevelSetWrapper: ", *args)


    def index(self, x : numpy.ndarray) -> tuple:
        """ Return grid index of state rounded to next grid index. """

        index = (x.ravel() - self.x_min) / self.dx     

        return tuple([math.ceil(idx) for idx in index]) 

    def index_valid(self, x : numpy.ndarray) -> tuple:
        """ Return only valid indices that exist in current grid. """
        index = self.index(x)

        if not self._index_in_grid(index):
            # Fail silently (see below for analysing new state set implementations)
            # print('Received index request: ', index)
            # print('Permitted (min | max): ({} | {})'.format(self.index_min, self.index_max))
            # self.print_config()
            raise pylevel.error.IndexNotInGridError()

        return index


    def state(self, index : numpy.ndarray) -> numpy.ndarray:
        """ Return state of grid index. """
        return numpy.array(index * self.dx + self.x_min)


@attr.s
class ReachableSetData:
    """ Collection of functions for reachable sets.

        Reads HDF5 file without writing. Wrapper and higher level objects
        will use read write for updating existing files.

    """
    ## Numerical grid interface of *.mat file provided data
    grid = attr.ib(type=Grid)

    ## LEGACY HDF5: /data group
    data_handle = attr.ib(type=typing.Optional[str])

    ## Time index to slice value function
    time_index = attr.ib(default=None)

    ## Value function
    value_function = attr.ib(default=None) # , type=typing.Optional[dask.array])

    ## Gradient
    # gradient = attr.ib(default=None, type=typing.Optional[dask.array])

    ## Select whether to verbosify prints
    debug_is_enabled = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        self._initialise_data_reference()
        self._extend_periodic_dimensions()

    def _initialise_data_reference(self):
        ## Initialise value_function with states of time index 0
        self.at_time(time_index=0)

    def _extend_periodic_dimensions(self):
        """ To be documented. (@Frank)

            Appends data columnvector to periodic data to allow
            differentiation.

            Note:
                Ported from Mo Chens augmentPeriodicData.m in helporOC git repo.
                Helps deal with periodic data axes.
        """
        g = self.grid
        # t = numpy.squeeze(numpy.asarray(g.dim, dtype=int))
        # print('Dim: ', t)

        for i in range(g.dim):
            ## TODO: Update check on periodic dim
            if g._is_dimension_periodic(i): #clunky...
                ## TODO: Check if this has been run before and if
                # tested remove exception
                raise NotImplementedError()
                g.vs[i] = numpy.append(g.vs[i], g.vs[i][-1] + g.dx[i])

                # create correct concatenation to make axes i "periodic"
                colon = slice(0, None)
                # colons = [colon for _ in range(g.dim)] + [numpy.newaxis]
                colons = [colon for _ in range(g.dim)]
                colons[i] = 0 # used to be 1, should be 0, but check later
                colons = tuple(colons)

                aug_shape = list(self.data.shape)
                aug_shape[i] = 1
                aug_shape = tuple(aug_shape)
                aug_dim_data = self.value_function[colons].reshape(aug_shape)

                ## TODO: where is data used
                self.value_function= numpy.concatenate(
                        (self.data, aug_dim_data),
                        axis = i)

    def _get_interpolated_value(self,
            x : numpy.ndarray,
            interpolation_method : InterpolationMethod = InterpolationMethod.Linear) \
                -> numpy.ndarray:
        """ Ported from Mo Chens eval_u.m in helperOC git repo.

            Note:
                Evaluates interpolated value from value function over grid.
        """
        g = self.grid
        ## Handle periodicity in input x
        for i in range(g.dim):
            if self._is_periodic_dim(i):
                period = max(g.vs[i]) - min(g.vs[i])

                i_above_bounds = x > max(g.vs[i])
                while i_above_bounds.any():
                    x[i_above_bounds] = x[i_above_bounds] - period
                    i_above_bounds = x > max(g.vs[i])

                i_below_bounds = x < min(g.vs[i])
                while i_below_bounds.any():
                    x[i_below_bounds] = x[i_below_bounds] + period
                    i_below_bounds = x < min(g.vs[i])

        # Build points tuple for interpolation
        points = []
        for i in range(g.dim):
            points.append(g.vs[i].reshape((g.vs[i].shape[0],)))
        points = tuple(points)

        ## TODO: Check if returning numpy value
        return interpn(points, self.data, x, method=method)[0]

    def _get_states_from_indices(self, indices : typing.List[int]) \
            -> typing.List[numpy.ndarray]:
        """ Return list of states for list of indices. """
        ## TODO: Return dask graph
        states = list()
        grid = self.grid
        for index in indices:
            grid_indices[index] = True
            state = grid.state(index)
            states.append(state)
        return states

    def sublevel_mask(self, level : float = 0.0,
            time_index : typing.Optional[int] = None) -> typing.List[tuple]:
        """ Return sublevel set incl. boundary

            Note:
                non-strict sublevel set

        """
        return self.value_function  <= level

    def sublevel_indices(self, level : float = 0.0,
            time_index : typing.Optional[int] = None) -> typing.List[tuple]:
        """ Return sublevel set incl. boundary

            Note:
                non-strict sublevel set

        """
        return dask.array.argwhere(self.value_function <= level)

    def sublevel(self, mask) -> typing.List[numpy.ndarray]:
        """ Return states of sublevel of level set. """
        return self.value_function[mask]

    def at_time(self, time_index):
        """ Create time index sliced dask array from HDF5 dataset handle. """
        ## This imports the value function in wrong shape => Transpose
        vf = self.data_handle['value_function']
        self.value_function = dask.array.from_array(vf).transpose()[..., time_index]

    def debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("ReachableSetData: ", *args)

