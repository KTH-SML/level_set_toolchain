#!/usr/bin/env python
""" Level set wrapper providing convenience methods. """


import sys
import attr
import dask
import enum
import time
import h5py
import numpy
import pickle
import typing
import dask.array
import dask.dataframe
from scipy.spatial import ConvexHull


import pylevel


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"

import pdb

@attr.s
class ReachableSetWrapper:
    """ Encapsulates convenience methods to access reachable sets.


        Defines HDF5 based data handle, numerical instances of grid
        specification and generates desired numerical sets using
        ReachableSetWrapper methods, which is based on dask computational
        graphs for possibly distributed and larger than memory computations.


        Note:
            Initialise using previously exported `*.levelset` using
            the `from_memory` argument or parse a label and path to
            initialise from a `*.mat` file.

            ReachableSetData provides access to grid indices and their
            respective states using Grid, value function values or sublevel sets.

            On initialisation for each discretised time step a
            ReachableSetData entry is added to the `sets` attribute.

        Note:
            Convexified returns a 2D representation in XY of the statespace
            where the non-convexified returns a boolean mask that has to be transformed
            into an index array and scaled by its physical dimension to received the state.

    """
    ## Initialisation arguments
    label = attr.ib(type=str)

    ## 1. (optional) Retrieve from memory using path to *.levelset binary
    from_memory = attr.ib(default=None, type=typing.Optional[str])

    ## 2. (optional) Initialisation from raw data using path to *.mat file
    path = attr.ib(default=None, type=typing.Optional[str])

    ## Data file
    # HDF5: file handle
    file_handle = attr.ib(default=None, type=typing.Optional[h5py.File])
    # HDF5: /data group
    data_handle = attr.ib(default=None, type=typing.Optional[h5py.File])

    ## Sets dictionary with (key,value) of type (time,LevelSetDict)
    ## -> The LevelSetDict consists of
    # keys: (grid_indices,states,value_function,ReachableSetData)
    # type: (list,numpy.array,dict,GridData)
    ## TODO: Append to hdf as /wrapper/subsets/time_idx = h5py.h5r.Reference
    sets = attr.ib(
            default=None,
            type=typing.Optional[typing.Dict[float, pylevel.data.ReachableSetData]])

    ## Raw data handle
    ## Value function data
    # HDF5: /data/value_function dataset (sliced in time [..., time_index]
    value_function = attr.ib(
            default=None,
            type=typing.Optional[typing.Dict[tuple, numpy.ndarray]])

    ## Time data
    # HDF5: /data/time dataset
    time = attr.ib(default=None, type=typing.Optional[typing.List[int]])

    ## Maximal time to reach
    maximum_time_to_reach = attr.ib(default=None, type=typing.Optional[float])

    ttr = attr.ib(default=None, type=typing.Optional[h5py.Group])

    grad = attr.ib(default=None, type=typing.Optional[h5py.Group])

    ## Massaged data groups (of datasets)
    group_wrapper = attr.ib(default=None, type=typing.Optional[h5py.Group])
    ## List of datasets with sparse boolean arrays
    group_subsets = attr.ib(default=None, type=typing.Optional[h5py.Group])
    ## List of datasets with sparse boolean arrays of convexified subsets
    group_subsets_convexified = attr.ib(default=None, type=typing.Optional[h5py.Group])

    ## Gradient data
    grad_dataset = attr.ib(default=None, type=typing.Optional[h5py.Group])

    ## Minimume time-to-reach data
    min_ttr_dataset = attr.ib(default=None, type=typing.Optional[h5py.Group])

    ## Grid utility object
    grid = attr.ib(default=None, type=typing.Optional[pylevel.data.Grid])

    ## State set type (optional)
    state_set_type = attr.ib(default=None, type=typing.Optional[enum.IntEnum])
    ## Safety priority (optional for avoid sets) (set from external)
    safety_priority = attr.ib(default=1, type=int)
    ## Show config by default
    show_config = attr.ib(default=True, type=bool)
    ## Visualise grid initialisation
    visualise_grid = attr.ib(default=False, type=bool)

    ## Export if load_from memory is not provided or fails
    initialise_once = attr.ib(default=True, type=bool)

    ## Force reinitialisation
    force_initialisation = attr.ib(default=False, type=bool)

    ## Verbosify debug prints
    debug_is_enabled = attr.ib(default=False, type=bool)

    ## Expose storage requirements on initialisation
    verbosify_storage = attr.ib(default=True, type=bool)

    def __attrs_post_init__(self):
        ## Access HDF5 file
        self._access_data_file()

        if not self.is_initialised or self.force_initialisation:
            self._initialise_data()

        ## TODO: Decide whether to load in-memory
        # self._activate_data()

    def _access_data_file(self):
        """ Access data file and recover meta data. """
        self._debug('Access HDF5 data at:\n{}'.format(self.path))

        ## TODO: Use distributed computing for large files
        # Create client and assign computing resources (build graph in initialiser)
        # client = Client(n_workers=2, threads_per_worker=2, memory_limit='2GB')
        # print('-> Connect to distributed client with: ', client)

        ## Initialise common data handles
        self._activate_data_handles()

        ## Fetch meta data from data group
        self.is_initialised = self.data_handle.attrs.get(
                'is_initialised', False)
        self.timestamp_initialisation = self.data_handle.attrs.get(
                'timestamp_initialisation', None)

        if self.is_initialised:
            ## Pre-access some data
            self.ttr = self.min_ttr_dataset["min_ttr"]
            self.grad = self.grad_dataset["grad"]

        print('Is initialised: ', self.is_initialised)
        print('Force initialisation: ', self.force_initialisation)

    def _initialise_data(self):
        """ Initialise wrapper specific data. """
        ## Initialise loader (without storing raw data reference)
        self._debug("Initialise from: {}".format(self.path))

        ## Fetch hdf5 data group
        data = self.data_handle

        # States
        self._initialise_sets()

        ## Set data group metadata
        data.attrs['is_initialised'] = True
        data.attrs['timestamp_initialisation'] = time.time()
        self._debug('Data initialised: \t{} (timestamp: {})'.format(
            data.attrs['is_initialised'],
            data.attrs['timestamp_initialisation']))
        ## Close file
        self.file_handle.close()

        ## Reopen saved file
        self._activate_data_handles()

        ## Pre-access some data
        self.ttr = self.min_ttr_dataset["min_ttr"]
        self.grad = self.grad_dataset["grad"]

    def _initialise_sets(self):
        """ Iterate over discretised time and initialise corresponding ttr.

            Todo:
                Possible to collect all pending dask graphs as computation and
                execute parallelised as from_delayed.

        """

        ## Fetch initialised grid utility
        grid = self.grid

        ## Open HDF5 file for updates
        # LEGACY data = h5py.File(self.path, mode='r+')
        data = self.data_handle

        group_wrapper = self.group_wrapper
        group_subsets= self.group_subsets
        group_subsets_convexified = self.group_subsets_convexified
        grad_dataset = self.grad_dataset
        min_ttr_dataset = self.min_ttr_dataset

        self._debug('ReachableSetWrapper initialising data for {}'.format(
            group_wrapper.keys()))

        ## Ordered dictionary for time sequence preservance in ttr search
        ## LEGACY tbs = 0

        ## Initialise reacheble set data utility
        state_set_data = pylevel.data.ReachableSetData(
                grid=grid,
                data_handle=self.data_handle)

        ## Compute and store gradient
        ti = time.time()
        vf = dask.array.from_array(state_set_data.at_all_time()).transpose()
        grad = numpy.array([gradient.compute()
                            for gradient in dask.array.gradient(vf)])
        self._debug('Gradient computation took : ', time.time() - ti)
        grad_data = grad_dataset.require_dataset(
                "grad",
                grad.shape,
                dtype='f',
                compression='gzip')
        grad_data[...] = grad

        ## Initialize min ttr dask array
        min_ttr_darray = float("inf") * dask.array.ones(state_set_data.value_function.shape)

        t0 = time.time()
        ## TODO: Check the time sequence (t0 to tf or flipped)
        for time_index, time_stamp in enumerate(self.time):
            print('{} - Compute level set at time: {}'.format(time.time() - t0, time_stamp))
            stamp = time.time()
            self._debug('Initialising time index {} of {}'.format(
                time_index, len(self.time) - 1))

            self._reset_datasets_of_index(
                    time_index=time_index,
                    wrapper_data_handle=group_wrapper)

            ## Slice data of interest
            state_set_data.at_time(time_index)
            ti = time.time()
            subset_mask = state_set_data.sublevel_mask(
                    level=0.0,
                    time_index=time_index)

            self._debug('Subset mask took : ', time.time() - ti)

            ## Compute dask graph
            subset_data = subset_mask.compute()
            self._debug('Subset mask computation  took : ', time.time() - ti)

            ## Compute current ttr dask array
            ttr_darray = subset_mask
            ttr_darray[ttr_darray == False] = float("inf")
            ttr_darray[ttr_darray == True] = time_stamp
            min_ttr_darray = dask.array.fmin(min_ttr_darray, ttr_darray)

            ## Skip empty level sets
            if not subset_data.any():
                print('Skip subset:')
                continue

            ## TODO: LEGACY (sparse) - Unused
            # subset_mask.map_blocks(sparse.COO)
            # subset_data = sparse.COO(subset_mask.compute())
            # subset_data = subset_mask.compute()

            ## Store sparse subset mask
            # subset_mask.map_blocks(sparse.COO)
            subset = group_subsets.require_dataset(
                    str(time_index),
                    subset_data.shape,
                    dtype='?',
                    compression='gzip')
            subset[...] = subset_data

            ## Return indices of active states
            ti = time.time()
            indices = dask.array.argwhere(subset_data).compute()
            self._debug('Indices took : ', time.time() - ti)

            ti = time.time()
            ## Attempt to simplify state conversion by selecting only simplices
            # Only useful if apply_along_axis conversion becomes not scalable
            if False:
                ## TODO: Test indices convexified
                hull = ConvexHull(indices)
                simplices = hull.points[hull.simplices.flat, :]
                simplices = numpy.array(simplices)
                ## print('Simplices shape: ', simplices.shape)

                states = dask.array.apply_along_axis(
                        grid.state,
                        axis=1,
                        arr=simplices).compute()
            else:
                states = dask.array.apply_along_axis(
                        grid.state,
                        axis=1,
                        arr=indices).compute()
            self._debug('States took : ', time.time() - ti)

            if True:
                try:
                    ti = time.time()
                    ## Generate 2D projection of states
                    print('Shape of states: ', states.shape)
                    states_sliced = numpy.hstack([
                        states[:, [0]],
                        states[:, [2]]])

                    hull = ConvexHull(states_sliced)
                except Exception as e:
                    import matplotlib.pyplot as plt
                    # plt.plot(states_sliced)
                    plt.scatter(x=states_sliced[:,[0]],y=states_sliced[:,[1]])
                    plt.show()
                    print('Shape of states: ', states_sliced.shape)


                #vertices = [hull.points[[i], :].reshape(-1, 1)
                #                 for i in hull.vertices]
                vertices = hull.points[hull.vertices.flat, :]

                vertices = numpy.squeeze(numpy.array(vertices))

                subset_convexified = group_subsets_convexified.require_dataset(
                        str(time_index),
                        vertices.shape,
                        dtype='f',
                        compression='gzip')
                subset_convexified[...] = vertices
                self._debug('Dataset expansion took : ', time.time() - ti)

                if False:
                    import matplotlib.pyplot as plt

                    plt.clf()
                    plt.plot(states[:, 0], states[:, 2], 'ko', label='states')
                    # vertices = subset_convexified[...]
                    plt.plot(vertices[:, 0], vertices[:, 1], 'rx', label='vertices')

                    plt.xlabel("x [m]")
                    plt.ylabel("y [m]")
                    plt.legend()
                    plt.pause(.1)


            ## TODO: Analyse size of data
            def get_size(element):
                binary = pickle.dumps(element, protocol=4)
                return sys.getsizeof(binary)

            # print('Subset true: ', subset_data_dense[indices])
            # print(indices.compute()[...])
            # print('Size of states: ', get_size(states))
            # print('Size of indices: ', get_size(indices))
            # print('Size of sparse: ', get_size(subset_data))

            # print('Size of dense: ', get_size(subset_data_dense))
            # Dense is almost factor 10x larger than sparse (But sparse should be todense on retrieval)

            self._debug('--> Initialised in {}s'.format(time.time() - stamp))

            ebs = 0
            if False and self.verbosify_storage:
                elements = level_set_dict.keys()
                self._debug('----> Has elements: ', elements)
                for e in elements:
                    ## Element binary size
                    ebs = get_size(level_set_dict[e])
                    ## Total binary size
                    tbs += ebs
                    pass
                    ## TODO:
                    #self.debug('------> Element: {} \t size: {}'.format(
                    #    e, sys.getsize
                    #    ))

        ti = time.time()
        min_ttr_array = min_ttr_darray.compute()
        self._debug('Min TTR computation took : ', time.time() - ti)
        min_ttr_data = min_ttr_dataset.require_dataset(
                "min_ttr",
                min_ttr_array.shape,
                dtype='f',
                compression='gzip')
        min_ttr_data[...] = min_ttr_array

        self._debug('Has initialised: ', self.group_subsets.keys())
        self._debug('Has initialised: (convexified) ', self.group_subsets_convexified.keys())
        self._debug('All sets initialised.')

    def _reset_datasets_of_index(self, time_index, wrapper_data_handle):
        """ Resets datasets in existing HDF5 wrapper data group. """
        ## Reset existing wrapper datasets
        def delete_wrapper_data(group, dataset):
            try:
                del wrapper_data_handle[group][dataset]
            except KeyError as e:
                print(' '.join([group, dataset]), ' not reset. (Did not exist).')

        ## Not needed delete_wrapper_data('states', str(time_index))
        delete_wrapper_data('subsets', str(time_index))
        delete_wrapper_data('subsets_convexified', str(time_index))

    def _activate_data_handles(self):
        ## Open HDF5 file in read / write mode with H5FD_SEC2 driver (on-disk)
        file_handle = h5py.File(self.path, mode='r+')
        self.file_handle = file_handle
        data_handle = file_handle['/data']
        self.data_handle = data_handle
        self._debug('Retrieved data handle: ', data_handle)

        ## Fetch hdf5 grid group
        # Helper to access grid indices or states and their discretisation
        # Grid with ds dimensional array and Nx1, Nx2, Nx3, Nxn entries
        self.grid = pylevel.data.Grid(
                data_path=self.path,
                data_handle=data_handle,
                show_config=self.visualise_grid,
                debug_is_enabled=self.visualise_grid)

        ## Retrieve general data groups (ds, dt)
        self.value_function = numpy.array(dask.array.from_array(data_handle['value_function']).transpose())
        ## TBD: self.gradient = dask.array.from_array(data['gradient'])
        # self.grad = numpy.gradient(self.value_function)
        ## Available time discretisation indices
        time_array = dask.array.from_array(data_handle['time']).compute()
        self.time = numpy.squeeze(numpy.array(time_array).flatten())

        ## Ensure time is increasing with indices
        if self.time[0] > self.time[-1]:
            self.time = self.time.reverse()

        ## TODO: Find maximal ttr that is computed
        self.maximum_time_to_reach = self.time[-1]
        ## Initialise wrapper specific data groups
        ## Create wrapper data group to add datasets
        self.group_wrapper = data_handle.require_group("wrapper")
        ## Use to check membership
        # (dimensionality: argwhere encoding state membership) -> CSC sparse
        # (value function: boolean array)
        self.group_subsets = self.group_wrapper.require_group("subsets")
        ## For illustration purposes
        # same as above : convexified states
        self.group_subsets_convexified = self.group_wrapper.require_group("subsets_convexified")
        self.min_ttr_dataset = self.group_wrapper.require_group("min_ttr")
        self.grad_dataset = self.group_wrapper.require_group("grad")


    def _debug(self, *args):
        """ Print debug messages if debugging is enabled. """
        if self.debug_is_enabled:
            print("LevelSetWrapper: ", *args)

    def reach_at_t_idx(self, t_idx : int, convexified=False):
        """ Return reachable state set at time_idx. """
        if convexified:
            return self.group_subsets_convexified[str(t_idx)][...]
        return self.group_subsets[str(t_idx)][...]

    def reach_at_t(self,
            t : float,
            convexified=False):
        """ Return reachable set at time t.

            Note:
                Optionally only return convexified reachable set for
                visualisation purposes.
        """
        ts = numpy.array(self.time)
        t_idx = numpy.abs(ts - t).argmin()

        if t > self.time[-1]:
            self._debug('State not reachable within time: {}'.format(t))
            raise pylevel.error.StateNotReachableError()

        return self.reach_at_t_idx(t_idx, convexified)

    def reach_at_min_ttr(self,
            state : numpy.ndarray,
            convexified : bool=False):
        """ Return minimial time to reach set and its discretised time. """

        state_key = "states_convexified" if convexified else "states"

        index = self.grid.index_valid(state)

        ## Verify that time is closest to furthest
        # Assume goal set is not avoid set

        for t_idx, time_i in enumerate(self.time):
            self._debug('ReachableSetWrapper: Find min reach TTR at time index: {} at time {}s'.format(t_idx, time_i))
            try:
                state_set = self.group_subsets[str(t_idx)]

                if not state_set[index]:
                    continue
                self._debug('ReachableSetWrapper: Found state {} at time {}'.format(state, time_i))

                if convexified:
                    state_set = self.group_subsets_convexified[str(t_idx)][...]

                self._debug('ReachableSetWrapper: Min reach TTR state found in ', time_i)

                return state_set, time_i
            except (LookupError, ValueError) as e:
                pass
                # import traceback
                # self._debug(traceback.print_tb(e.__traceback__))

        self._debug('ReachableSetWrapper: Failed to find index in any set.',
            'Unreachable state.')

        raise pylevel.error.StateNotReachableError()

    def min_ttr(self, state : numpy.ndarray):
        """ Return minimal time to reach discretized time.

        This method is faster than reach_at_min_ttr, since it uses a
        lookup table"""
        index = self.grid.index_valid(state)
        return self.ttr[index]

    def is_member(self, state: numpy.ndarray, return_time_to_reach=False) -> numpy.float:
        """ Return if state is not member of any reachable state sets. """
        index = self.grid.index_valid(state.flatten())

        for time_idx, time_i in enumerate(self.time):
            try:
                state_set = self.group_subsets[str(time_idx)][...]
                if not state_set[index]:
                    continue

                # print('Found member of ', self.state_set_type, ' (at time {})'.format(time_i))

                if return_time_to_reach:
                    return True, time_i

                return True
            except LookupError as e:
                # self._debug("Failed to find index in {}".format(time_idx))
                pass

        self._debug('ReachableSetWrapper: Failed to find index in any set.')
        raise pylevel.error.StateNotReachableError()

    def is_not_member(self, state: numpy.ndarray) -> numpy.float:
        """ Return if state is not member of any reachable state sets. """

        return not self.is_member(state)

    def gradient(self,
            state: numpy.ndarray,
            ttr : float,
            axis : int) -> numpy.ndarray:
        """ Return gradient of current state for specified axes.
        """
        # TODO: normalized : bool = False)
        axis = ((axis), )
        index = self.grid.index_valid(state)
        time_index = ((numpy.abs(self.time - ttr)).argmin(),)
        grad = self.grad[axis+index+time_index]
        # grad = self.grad[axis][index + time_index]
        # if normalized:
            # if grad < 0.0:
                # most_negative_grad = numpy.min(self.grad[axis])
                # grad = grad / abs(most_negative_grad)
            # elif grad > 0.0:
                # most_positive_grad = numpy.max(self.grad[axis])
                # grad = grad / most_positive_grad
        return grad

    # def gradient_drone(self,
            # state: numpy.ndarray,
            # ttr : float,
            # axes : typing.Optional[typing.List[int]] = None,
            # normalised : bool = False) -> numpy.ndarray:
        # """ Return gradient of current state for specified axes.

            # Note:
                # To only use directional information use the `normalised`
                # argument and return the gradient unit vector instead.

        # """

        # ## TODO: Generating reach sets to debug
        # # Look up value function for grid
        # index = self.grid.index_valid(state)

        # ## Current state value function
        # time_index = tuple(numpy.where(self.time == ttr)[0])
        # v = self.value_function[index + time_index]

        # try:
            # ## List of neighbor indices (4)
            # # Amount of indices times state space dim: di x ds
            # indices, indices_delta = self.grid.index_neighbours(
                    # index, axes=axes, return_offset=True)
        # except IndexHasNoValidNeighboursError as e:
            # return numpy.zeros((2, 1))

        # ## TODO: Remove me
        # # print('--> Index ({}) has {} neighbours: \n{}\n'.format(
        # #      index, len(indices), indices))

        # ## di x 1 : scalar spatial magnitude for each index
        # dsi = numpy.linalg.norm(indices_delta * self.grid.dx, axis=1)

        # ## di x 1 : value function differential for each index
        # vs = numpy.apply_along_axis(
                # lambda index: self.value_function[tuple(index) + time_index] - v, arr=indices, axis=1)
        # ## di x 1 / di x 1 : gradient for each index based on its spatial magnitude
        # gs = numpy.divide(vs, dsi)
        # vector = numpy.multiply(indices_delta[numpy.argmax(gs)], self.grid.dx)

        # ## TODO: Drone specific implementation for xy-plane
        # # vector = numpy.array([vector[0], vector[2]])
        # # if normalised:
            # # n = numpy.linalg.norm(vector, ord=2)
            # # if n == 0:
                # # n = numpy.finfo(vector.dtype).eps
            # # vector /= n
        # return vector


