#!/usr/bin/env python
""" Example for level set wrapper usage.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""


import numpy


import pylevel


# FORCE_INITIALISATION = False
FORCE_INITIALISATION = True
EXEMPLIFY_DEBUG_VERBOSITY = True


if __name__ == '__main__':
    # level_set_type = pylevel.datasets.LevelSetExample.BenchmarkLowResLowHoriz
    level_set_type = pylevel.datasets.LevelSetExample.BenchmarkMediumResMediumHoriz
    # level_set_type = pylevel.datasets.LevelSetExample.BenchmarkHighResMediumHoriz

    wrapper = pylevel.wrapper.ReachableSetWrapper(
            label="ExampleLevelSet",
            path=pylevel.datasets.path[level_set_type],
            debug_is_enabled=EXEMPLIFY_DEBUG_VERBOSITY,
            force_initialisation=FORCE_INITIALISATION)

    ## Time steps from final time tf to t0
    t_idx = list(wrapper.time)
    t_idx.reverse()
    t_idx_sel = t_idx[0]

    ## Time indexed access of levelsets
    print('Time horizon :\n', t_idx)
    print('--> Select time index : ', t_idx_sel)
    reachable_states = wrapper.reach_at_t(t_idx_sel)
    states_sliced = reachable_states
    # states_sliced = numpy.hstack([
    #     reachable_states[:, [0]],
    #     reachable_states[:, [2]]])

    pylevel.utilities.visualise_2d(wrapper, states_sliced, t_idx_sel, show=False, show_image=False)
    pylevel.utilities.show_plots_for_time(time_in_seconds=.5)

    pylevel.utilities.show_plots()

