#!/usr/bin/env python
""" Example for level set wrapper usage.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""

import os
import numpy


import pylevel


if __name__ == '__main__':
    wrapper = pylevel.wrapper.LevelSetWrapper(dataset=pylevel.datasets.LevelSet.Drone)

    state = [-0.2, 0.0, 0.2, 0.0]
    states, time = wrapper.get_reachable_set(state)
    pylevel.utilities.visualise_2d(wrapper, states, time)

    # states1 = wrapper.get_reachable_set_at_time(5)
    # states2 = wrapper.get_reachable_set_at_time(3)
    # states3 = wrapper.get_reachable_set_at_time(2)
    # states4 = wrapper.get_reachable_set_at_time(1)
    # pylevel.utilities.visualise_2d(states1, wrapper, show=False)
    # pylevel.utilities.visualise_2d(states2, wrapper, show=False)
    # pylevel.utilities.visualise_2d(states3, wrapper, show=False)
    # pylevel.utilities.visualise_2d(states4, wrapper)

