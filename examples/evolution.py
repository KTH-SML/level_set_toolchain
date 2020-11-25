#!/usr/bin/env python
""" Example for level set wrapper usage.

    Author: Philipp Rothenhäusler, Stockholm 2020

"""

import os
import numpy


import pylevel


if __name__ == '__main__':
    wrapper = pylevel.wrapper.LevelSetWrapper(dataset=pylevel.datasets.LevelSet.Drone)

    # Test sequence of sets
    t_idx = numpy.linspace(0,1,10)
    sets = [wrapper.get_reachable_set_at_time(t) for t in t_idx]
    for set_element, t in zip(sets,t_idx):
        print(numpy.shape(set_element))
        pylevel.utilities.visualise_2d(wrapper, set_element, t, show=False, show_image=False)
    pylevel.utilities.show_plots()

