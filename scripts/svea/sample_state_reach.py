#!/usr/bin/env python3

import os
import time
import numpy as np
import matplotlib.pyplot as plt

import pylevel
cwd = os.path.dirname(os.path.abspath(__file__))
# change this path to whatever reachset .mat file you want
svea_reach_path = cwd + "/../../resources/generated/svea/svea_reach.mat"

from utils import animate_reachset_evolution, viz_reachset

if __name__ == "__main__":
    # load reach set from .mat file
    tic = time.time()
    reach = pylevel.wrapper.ReachableSetWrapper(
        label = "SVEA Reach",
        path = svea_reach_path,
        debug_is_enabled=True)
    print("Took {0}s to load reachsets from memory".format(time.time()-tic))

    # pick states to sample
    states = [
        np.array([-1.0, 1.0, 180.0, 0.0]),
        np.array([1.0, 0, -135.0, 0.2]),
    ] # [m, m, degrees, m/s]

    for state in states:
        target_set_plt = plt.Circle((0, 0), 0.5, color='r', alpha = 0.5)
        viz_reachset(reach, state, show=False, show_timing=True,
                        target_plt = target_set_plt)
        pylevel.utilities.show_plots_for_time(time_in_seconds=.3)
    pylevel.utilities.show_plots()
