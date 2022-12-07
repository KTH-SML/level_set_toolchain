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

    viz_heading = -45.0 # degrees
    viz_vel = 0.5 # m/s
    target_set_plt = plt.Circle((0, 0), 0.5, color='r', alpha = 0.5)
    print("Animating reach set evolution at yaw={0} [deg] vel={1} [m/s]".format(
            viz_heading, viz_vel))
    ax = animate_reachset_evolution(reach, viz_heading, viz_vel,
                                    target_plt = target_set_plt)
