#!/usr/bin/env python
"""
Examples of working with value function solutions to the HJI inequality
over time, and with a value function that has been optimized across time
already. quad4D BRS is a backward reach set, SVEA TTR is the set of
minimum time to reach an avoid set.

Author: Frank Jiang, Stockholm 2020
Author: Philipp Rothenhäusler, Stockholm 2020

"""

import os
import numpy as np
from scipy.io import loadmat
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
plt.style.use('seaborn-muted')

import pylevel

path = os.path.dirname(os.path.abspath(__file__))
# for RS example
quad_BRS_file = path + "/../resources/quad4D/low_res_BRS.mat"

def build_state_to_reachset_dict(BRS_list, in_reach_set_idx):
    # TODO: too slow
    state_to_reachset_dict = {}
    n_x = BRS_list[0].N[0]
    n_y = BRS_list[0].N[1]
    n_vx = BRS_list[0].N[2]
    n_vy = BRS_list[0].N[3]
    for x_ind in range(n_x):
        for y_ind in range(n_y):
            for vx_ind in range(n_vx):
                for vy_ind in range(n_vy):
                    ind = (x_ind, y_ind, vx_ind, vy_ind)
                    not_in_brs = True
                    for i in range(len(BRS_list)):
                        if ind in in_reach_set_idx[i]:
                            reach_set_pts =  np.array(in_reach_set_idx[i])
                            xy_pts = reach_set_pts[:, 0:2]
                            state_to_reachset_dict[ind] = xy_pts
                            not_in_brs = False
                            break
                    if not_in_brs:
                        state_to_reachset_dict[ind] = np.array([])
    return state_to_reachset_dict

def find_xy_reach_set(state, grid_handler, in_reach_set_idx):
    """Find earliest BRS that state is a member of"""
    xy_pts = np.array([])
    for i, idx_set in enumerate(in_reach_set_idx):
        ind = grid_handler.get_idx(state)
        if ind in idx_set:
            pts = np.array(idx_set)
            xy_pts = pts[:, 0:2]
            break
    return xy_pts, i

def in_hull(idx, hull):
    """Check if in all half-spaces"""
    eqs = hull.equations
    inside_eqs = []
    for eq in eqs:
        total = 0
        for i, ind in enumerate(idx):
            coeff = eq[i]
            total += coeff * ind
        inside_eqs.append(total < -eq[-1])
    return np.all(np.array(inside_eqs))

def hull_img(hull, w, h):
    """Compute image of hull"""
    grid_explicit = np.empty((w, h),
                                dtype = object)
    grid_explicit[:, :] = [[(i, j) for i in range(w)]
                            for j in range(h)]
    in_hull_f = lambda x: float(in_hull(x, hull))
    in_hull_vectorized = np.vectorize(in_hull_f)
    grid_explicit = grid_explicit.flatten()
    hull_in_grid_img = in_hull_vectorized(grid_explicit)
    hull_in_grid_img = hull_in_grid_img.reshape((w, h))
    return hull_in_grid_img

def main():
    # load from MATLAB files
    print('# Loading for MATLAB files')
    quad_BRS_data = loadmat(quad_BRS_file)

    print('# Building Reachable Sets')
    # RS solutions over time for quadrotor in 2D plane
    BRS_grid = quad_BRS_data['g']
    grid_helper = pylevel.grid.Grid(BRS_grid)
    BRS_val_funcs = quad_BRS_data['BRS_data'] # one valfunc per time step
    BRS_times = quad_BRS_data['BRS_time'].tolist()[0]
    BRS_list = []
    in_reach_set_idx = [] # list of list of indices inside reach set
    for i in range(len(BRS_times)):
        BRS = pylevel.grid.GridData(BRS_grid, BRS_val_funcs[:, :, :, :, i])
        BRS_list.append(BRS)
        # 1 - in sublevel set, 0 - not in sublevel set
        in_reach_set_idx.append(BRS.sublevel_set_idx(level=0.0))

    # state_to_reachset = build_state_to_reachset_dict(BRS_list, in_reach_set_idx)
    state = [-0.2, 0.0, 0.2, 0.0]
    xy_pts, reach_set_ind = find_xy_reach_set(state, grid_helper,
                                              in_reach_set_idx)
    # xy_pts = state_to_reachset[grid_helper.get_idx(state)]
    reach_set_t = -BRS_times[reach_set_ind]

    found_BRS =  len(xy_pts) != 0
    if found_BRS:
        convex_hull = ConvexHull(xy_pts)

        img_width = grid_helper.N[0]
        img_height = grid_helper.N[1]
        img = hull_img(convex_hull, img_width, img_height)

        t_str = "t={} [s]".format(reach_set_t)
        plt.title("Convex Hull of Backward Reach Set at " + t_str)
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
        plt.plot(xy_pts[:,0], xy_pts[:,1], 'ko')
        hull_set = convex_hull.points
        hull_vertices = np.stack(
                [hull_set[idx] for idx in convex_hull.vertices], axis=1)
        plt.scatter(*hull_vertices.tolist() , c='g', s=200)
        plt.plot(*hull_vertices.tolist(), 'r--', linewidth=3, alpha=0.3)
        plt.imshow(img, "gray", alpha = 0.4)
        plt.show()
    else:
        print ('Given state not in any reach set')

if __name__ == '__main__':
    main()
