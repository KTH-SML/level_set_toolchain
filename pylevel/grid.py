# -*- coding: utf-8 -*-
"""
Grid module containing classes that work with saved MATLAB outputs of
the Level Set Toolbox and helperOC. Much of the work is ported from
helperOC into Python, with some additional convenience features added
in.
"""

import attr
import typing
import numpy
# Legacy
import numpy as np
from scipy.interpolate import interpn

__license__ = "MIT"
__author__ = "Frank Jiang, Philipp Rothenhäusler"
__maintainer__ = "Frank Jiang"
__email__ = "frankji@kth.se "
__status__ = "Development"


@attr.s
class Grid:
    '''Python object version of HJB toolbox grids'''

    grid = attr.ib(type=numpy.array)
    debug_is_enabled = attr.ib(default=False, type=bool)
    show_config = attr.ib(default=False, type=bool)

    def __attrs_post_init__(self):
        '''Fills object based on input matlab grid numpy array imported by
        scipy.io.loadmat
        '''
        g = self.grid[0][0]
        # dimension of state space
        self.dim = g[0][0][0]
        # min grid corner
        self.min = g[1].reshape((self.dim,)).tolist()
        # max grid corner
        self.max = g[2].reshape((self.dim,)).tolist()
        # number of grid cells along each axis
        self.N = g[3].reshape((self.dim,)).tolist()
        # Boundary condition to specify behaviour
        self.bdry = g[4].reshape((self.dim,)).tolist()
        # step size along each axis
        self.dx = g[5].reshape((self.dim,)).tolist()
        # Convenience variable ds dimensional
        # grid index to state
        self.vs = g[6].reshape((self.dim,)).tolist()
        ## Unused - kept as reference: to be documented
        # self.xs = g[7].reshape((self.dim,)).tolist()
        ## Unused - kept as reference: to be documented
        # self.bdryData = g[8].reshape((self.dim,)).tolist()
        ## Unused - kept as reference: same info as N
        # self.shape = tuple(g[10][0].tolist())

        if self.show_config:
            print('Grid initialisation with:')
            print('Dimension:', self.dim)
            print('Grid (min | max): ({} | {})'.format(self.min, self.max))
            print('Grid step size: ', self.dx)

    def _assert_valid_state(self, x):
        assert len(x) == self.dim, "Input is wrong dimension"
        assert self.in_grid(x), \
               "Given state {0} not in grid ({1} - {2})".format(x,
                                                                self.min,
                                                                self.max)

    def _assert_valid_idx(self, idx):
        assert len(idx) == self.dim, "Input is wrong dimension"

    def in_grid(self, x):
        assert len(x) == self.dim, "Input is wrong dimension"
        if not np.isnan(np.sum(np.array(x))):
            above_min = np.array(x) > np.array(self.min)
            below_max = np.array(x) < np.array(self.max)
            return above_min.all() and below_max.all()
        else:
            return False

    def _is_periodic_dim(self, dim):
        return "addGhostPeriodic" in self.bdry[dim][0][0][3][0][0][0][0]

    def get_index_of_rounded_state(self, x):
        self._assert_valid_state(x)
        index = list()
        for i in range(len(x)):
            dx = self.dx[i]
            index.append(int(round((x[i] - self.min[i])/dx)))
        return tuple(index)

    def get_state_of_index(self, index):
        self._assert_valid_idx(index)
        state = []
        # dimensions
        for di in range(len(index)):
            # Get dimension-based grid step size
            dx = self.dx[di]
            state.append(index[di] * dx + self.min[di])
        return state

    # LEGACY
    def get_idx(self, x):
        self._assert_valid_state(x)
        idx = []
        for i in range(len(x)):
            dx = self.dx[i]
            idx.append(int(round((x[i] - self.min[i])/dx)))
        return tuple(idx)

    # LEGACY
    def get_state(self, idx):
        self._assert_valid_idx(idx)
        state = []
        # dimensions
        for di in range(len(idx)):
            # Get dimension-based grid step size
            dx = self.dx[di]
            state.append(idx[di] * dx + self.min[di])
        return state


@attr.s
class GridData(Grid):
    ''' Encapsulates functions for both grid and data functions on
        imported MATLAB data.

    '''
    ## Value function entries for meshed state space with
    ## indices according to grid_indices
    data = attr.ib(default=None, type=typing.Optional[numpy.array])

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self._augmentPeriodicData()

    def _augmentPeriodicData(self):
        '''Ported from Mo Chens augmentPeriodicData.m in helporOC git
        repo.

        Helps deal with periodic data axes.
        '''

        for i in range(self.dim):
            if self._is_periodic_dim(i): #clunky...
                self.vs[i] = np.append(self.vs[i], self.vs[i][-1] + self.dx[i])

                # create correct concatenation to make axes i "periodic"
                colon = slice(0, None)
                # colons = [colon for _ in range(self.dim)] + [np.newaxis]
                colons = [colon for _ in range(self.dim)]
                colons[i] = 0 # used to be 1, should be 0, but check later
                colons = tuple(colons)

                aug_shape = list(self.data.shape)
                aug_shape[i] = 1
                aug_shape = tuple(aug_shape)
                aug_dim_data = self.data[colons].reshape(aug_shape)

                self.data = np.concatenate(
                        (self.data, aug_dim_data),
                        axis = i)

    def get_raw_value(self, x):
        idx = self.get_idx(x)

        return self.data[idx]

    def get_interp_value(self, x, method='linear'):
        '''Ported from Mo Chens eval_u.m in helperOC git repo.

        Evaluates interpolated value from value function over grid.
        '''

        if type(x) == type([]):
            x = np.array(x).reshape((1, self.dim))
        else:
            assert type(x) == type(np.array([])), \
                   "Input x should be list or numpy array, gave a {0}".format(type(x))
            assert len(x.shape) <= 2, "Input x should be vector"
            assert max(x.shape) == self.dim, \
                    "Input x (dim={0}) wrong dimension".format(max(x.shape))

            if len(x.shape) == 1:
                x = x.reshape((1, self.dim))

        # handle periodicity in input x
        for i in range(self.dim):
            if self._is_periodic_dim(i):
                period = max(self.vs[i]) - min(self.vs[i])

                i_above_bounds = x > max(self.vs[i])
                while i_above_bounds.any():
                    x[i_above_bounds] = x[i_above_bounds] - period
                    i_above_bounds = x > max(self.vs[i])

                i_below_bounds = x < min(self.vs[i])
                while i_below_bounds.any():
                    x[i_below_bounds] = x[i_below_bounds] + period
                    i_below_bounds = x < min(self.vs[i])

        # build points tuple for interpn
        points = []
        for i in range(self.dim):
            points.append(self.vs[i].reshape((self.vs[i].shape[0],)))
        points = tuple(points)

        return interpn(points, self.data, x, method=method)[0]

    def sublevel_set_idx(self, level=0.0):
        """Return sublevel set incl. boundary (non-strict sublevel set)
        """
        index_array = np.where(self.data <= level)
        indices = []
        for i in range(len(index_array[0])):
            curr_index = [index_array[j][i] for j in range(len(index_array))]
            indices.append(tuple(curr_index))
        return indices

    def superlevel_set_idx(self, level=0.0):
        """Return superlevel set incl. boundary (non-strict superlevel
        set)"""
        index_array = np.where(self.data >= level)
        indices = []
        for i in range(len(index_array[0])):
            curr_index = [index_array[j][i] for j in len(index_array)]
            indices.append(tuple(curr_index))
        return indices
