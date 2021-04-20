#!/usr/bin/env python
""" Grid module providing objects to interface with imported *.mat file.

    Grid module containing classes that work with saved MATLAB outputs
    of the Level Set Toolbox and helperOC.
    Much of the work is ported from helperOC into Python,
    with some additional convenience features added in.

"""

import attr
import enum
import numpy
import typing
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
    """ Grid component for interfacing *.mat level sets. """

    ## Discretisation grid
    grid = attr.ib(type=numpy.array)
    ## Dimension of state space
    dim = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Minimum state value on grid start
    x_min = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Maximum state value on grid end
    x_max = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Count of grid elements along each dimensio
    N = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Boundary condition to specify behaviour
    boundary = attr.ib(default=None, type=typing.Optional[typing.List])
    ## Grid discretisation step along each dimension
    dx = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Convenience variable ds dimensional
    ## TODO: To be documented -> maybe good to choose a more expressive name
    vs = attr.ib(default=None, type=typing.Optional[numpy.ndarray])
    ## Enable debugging
    debug_is_enabled = attr.ib(default=False, type=bool)
    ## Show configuration
    show_config = attr.ib(default=False, type=bool)

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
        g = self.grid[0][0]

        self.dim = g[0][0][0]
        self.x_min = g[1].reshape((self.dim,))
        self.x_max = g[2].reshape((self.dim,))
        self.N = g[3].reshape((self.dim,))
        self.boundary = g[4].reshape((self.dim,)).tolist()
        self.dx = g[5].reshape((self.dim,))
        self.vs = g[6].reshape((self.dim,))

        if self.show_config:
            self.print_config()

    def print_config(self, x : typing.Optional[numpy.ndarray] = None):
        """ Visualise configuration and current state index. """
        if x is None:
            if not is_in_grid(x):
                print('State not in grid:')
            else:
                print('State in grid:')
            print('--> State index: ', self.index(x))

        print('Grid configuration:')
        print('Dimension:', self.dim)
        print('Grid (min | max): ({} | {})'.format(self.x_min, self.x_max))
        print('Grid step size: ', self.dx)

    def _is_state_in_grid(self, x : numpy.ndarray) -> bool:
        """ Return true if state is in discretisation range. """
        if not numpy.isnan(numpy.sum(numpy.array(x))):
            above_min = numpy.array(x) > numpy.array(self.x_min)
            below_max = numpy.array(x) < numpy.array(self.max)
            return above_min.all() and below_max.all()
        else:
            return False

    def _is_periodic_dim(self, dim: None) ->  bool:
        """ Docstring missing. """
        ## TODO: Document dim type or format
        return "addGhostPeriodic" in self.boundary[dim][0][0][3][0][0][0][0]

    def debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("LevelSetWrapper: ", *args)


    def _get_index_of_rounded_state(self, x : numpy.ndarray) -> tuple:
        """ Return grid index of state rounded to next grid index. """

        return tuple(((x - self.x_min) / self.dx).astype(int).flatten())

    def _get_state_of_index(self, index : tuple) -> numpy.ndarray:
        """ Return state of grid index. """
        state = numpy.array(index) * self.dx + self.x_min

        return numpy.array(state)

    @property
    def index(self):
        """ Return index from state input.  """

        return self._get_index_of_rounded_state

    @property
    def state(self):
        """ Convenience access for external access of grid methods.  """

        return self._get_state_of_index


@attr.s
class ReachableSetData:
    """ Collection of functions for reachable set at time discretisation.

        Note:
            Fundamental data placeholders are subclassed from Grid.

    """
    ## Grid interface of *.mat file provided data
    grid = attr.ib(type=Grid)

    ## Value function dictionary with (key, value) as type (grid_index, value_function)
    data = attr.ib(default=None, type=typing.Optional[numpy.array])

    ## Select whether to verbosify prints
    debug_is_enabled = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        self._augmentPeriodicData()

    def debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("ReachableSetData: ", *args)

    def _augmentPeriodicData(self):
        """ To be documented. (@Frank)

            Note:
                Ported from Mo Chens augmentPeriodicData.m in helporOC git repo.
                Helps deal with periodic data axes.
        """
        g = self.grid

        for i in range(g.dim):
            if g._is_periodic_dim(i): #clunky...
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
                aug_dim_data = self.data[colons].reshape(aug_shape)

                ## TODO: where is data used
                self.data = numpy.concatenate(
                        (self.data, aug_dim_data),
                        axis = i)

    def get_interpolated_value(self,
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

    def sublevel_set_idx(self, level=0.0):
        """ Return sublevel set incl. boundary

            Note:
                non-strict sublevel set

        """
        index_array = numpy.where(self.data <= level)
        indices = []
        for i in range(len(index_array[0])):
            curr_index = [index_array[j][i] for j in range(len(index_array))]
            indices.append(tuple(curr_index))
        return indices

    def superlevel_set_idx(self, level=0.0):
        """ Return superlevel set incl. boundary

            Note:
                non-strict superlevel set

        """
        index_array = numpy.where(self.data >= level)
        indices = []
        for i in range(len(index_array[0])):
            curr_index = [index_array[j][i] for j in len(index_array)]
            indices.append(tuple(curr_index))
        return indices

    def get_value_function_of_rounded_state(self,
            x : numpy.ndarray) -> numpy.ndarray:
        """ Return value function for closest grid index. """
        index = self.grid.index(x)

        try:
            return self.data[index]
        except Exception as e:
            self.grid.debug('Failed to find value function for state due to: ', e)
            self.grid.print_config(x)
            raise pylevel.error.StateLookupError()

    @property
    def sublevel_set(self):
        raise NotImplementedError()

    @property
    def superlevel_set(self):
        raise NotImplementedError()

    @property
    def value_function(self):
        """ Read-only return of value function. """
        return self.get_value_function_of_rounded_state
