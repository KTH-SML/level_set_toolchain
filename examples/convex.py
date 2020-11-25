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
