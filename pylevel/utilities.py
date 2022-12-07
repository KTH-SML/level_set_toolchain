#!/usr/bin/env python
""" Utility functions for level set wrapper.
"""

import numpy
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull


plt.style.use('seaborn-muted')


__license__ = "MIT"
__maintainer__ = "Frank Jiang"
__email__ = "fjiang@kth.se "
__status__ = "Development"


def visualize_XY(wrapper, states, time,
                 show=True, **plot_options):
    options = dict(cmap="red", alpha=0.3)
    options.update(plot_options)

    t_str = "t={} [s]".format(numpy.around(time,2))
    plt.title("Backward Reach Set at " + t_str)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.imshow(states.T, **options)
    plt.gca().invert_yaxis()

    if show:
        show_plots()

def visualize_hull_XY(wrapper, states, time,
                      show=True, show_image=False, **plot_options):
    grid = wrapper.grid
    options = dict(c=numpy.random.rand(3,),linewidth=3, alpha=0.3)
    options.update(plot_options)

    convex_hull = ConvexHull(states)

    if show_image:
        img_width = grid.N[0]
        img_height = grid.N[1]
        img = hull_img(convex_hull, img_width, img_height)
        plt.imshow(img, "gray", alpha = 0.4)

    t_str = "t={} [s]".format(numpy.around(time,2))
    plt.title("Convex Hull of Backward Reach Set at " + t_str)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.plot(states[:,0], states[:,1], 'ko')

    hull_set = convex_hull.points
    hull_vertices = numpy.stack(
            [hull_set[idx] for idx in convex_hull.vertices], axis=1)
    plt.legend()
    plt.fill(*hull_vertices.tolist(), label='Levelset_{}'.format(t_str), **options)
    plt.scatter(*hull_vertices.tolist(), c='g', s=200)
    plt.plot(*hull_vertices.tolist(), '--',**options)

    if show:
        show_plots()

def show_plots_for_time(time_in_seconds):
    plt.pause(time_in_seconds)

def show_plots():
    plt.grid()
    plt.show()


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
    return numpy.all(numpy.array(inside_eqs))



def hull_img(hull, w, h):
    """Compute image of hull"""
    grid_explicit = numpy.empty((w, h),
                                dtype = object)
    grid_explicit[:, :] = [[(i, j) for i in range(w)]
                            for j in range(h)]
    in_hull_f = lambda x: float(in_hull(x, hull))
    in_hull_vectorized = numpy.vectorize(in_hull_f)
    grid_explicit = grid_explicit.flatten()
    hull_in_grid_img = in_hull_vectorized(grid_explicit)
    hull_in_grid_img = hull_in_grid_img.reshape((w, h))

    return hull_in_grid_img

# LEGACY
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

