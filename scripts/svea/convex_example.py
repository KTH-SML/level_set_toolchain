#!/usr/bin/env python3

import os
import time
import numpy as np
from math import radians
import matplotlib.pyplot as plt

from scipy.spatial import ConvexHull

import pylevel
cwd = os.path.dirname(os.path.abspath(__file__))
# change this path to whatever reachset .mat file you want
svea_reach_path = cwd + "/../../resources/generated/svea/svea_reach.mat"


def convexified_reach_set(wrapper, state):
    # get correct value function
    ttr = reach.min_ttr(state) # time to reach [s]
    value_function = reach.reach_at_t(ttr)
    # get reach states (slice to reduce number of pts)
    _, _, yaw_index, v_index = reach.grid.index(state)
    sliced = value_function[:, :, yaw_index, v_index]
    reach_indices = np.argwhere(sliced > 0)
    aug_dim = (reach_indices.shape[0], 1)
    full_dim_reach_indices = np.hstack((
        reach_indices,
        yaw_index * np.ones(aug_dim),
        v_index * np.ones(aug_dim)
    ))
    # convert from grid indices to states
    reach_states = np.zeros(full_dim_reach_indices.shape)
    for i, index in enumerate(full_dim_reach_indices):
        reach_states[i, :] = reach.grid.state(index)
    reach_states_2D = np.hstack((
        reach_states[:, [0]],
        reach_states[:, [1]]
    ))
    # compute convex hull
    convex_hull = ConvexHull(reach_states_2D)
    return convex_hull, reach_states_2D, ttr


if __name__ == "__main__":
    # load reach set from .mat file
    tic = time.time()
    reach = pylevel.wrapper.ReachableSetWrapper(
        label = "SVEA Reach",
        path = svea_reach_path,
        debug_is_enabled=True)
    print("Took {0}s to load reachsets from memory".format(time.time()-tic))

    # pick state to sample
    state = np.array([-1.0, 1.0, 180.0, 0.5]) # [m, m, degrees, m/s]

    # compute hull at state
    convex_hull, states_XY, time_to_reach = convexified_reach_set(reach, state)

    # visualize_hull_XY re-computes hull and visualizes it
    pylevel.utilities.visualize_hull_XY(reach, states_XY, time_to_reach)
