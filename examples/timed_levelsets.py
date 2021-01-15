#!/usr/bin/env python
""" Example for level set wrapper usage.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""

import os
import numpy


import pylevel


if __name__ == '__main__':
    wrapper = pylevel.wrapper.LevelSetWrapper(dataset=pylevel.datasets.LevelSet.Drone)

    # Time steps from final time tf to t0
    t_idx = list(wrapper.time)
    t_idx.reverse()

    levelsets_states = [wrapper.get_reachable_set_at_time(t) for t in t_idx]
    for levelset_states, t in zip(levelsets_states,t_idx):
        states_sliced = numpy.hstack([
            levelset_states[:, [0]],
            levelset_states[:, [2]]])
        pylevel.utilities.visualise_2d(wrapper, states_sliced, t, show=False, show_image=False)
        pylevel.utilities.show_plots_for_time(time_in_seconds=.5)

    pylevel.utilities.show_plots()

