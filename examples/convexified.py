#!/usr/bin/env python
""" Example for level set wrapper usage.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""

import os
import numpy


import pylevel


if __name__ == '__main__':
    wrapper = pylevel.wrapper.LevelSetWrapper(
            dataset=pylevel.datasets.LevelSet.Drone,
            show_config=True)

    # px, vx, py, vy
    state = [-0.2, 0., 0.2, .0]
    states, time = wrapper.get_reachable_set(state)

    # Plot position in XY-plane
    states_sliced = numpy.hstack([states[:, [0]], states[:, [2]]])
    pylevel.utilities.visualise_2d(wrapper, states_sliced, time)
