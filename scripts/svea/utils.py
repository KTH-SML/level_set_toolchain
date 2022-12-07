import time
import numpy as np
from math import radians
import matplotlib.pyplot as plt

import pylevel


def viz_reachset(wrapper, state, show=True, show_timing=False, target_plt=None):
    tic = time.time() # TODO: replace with proper timing
    times = {"ttr": None, "set": None, "grad": None, "viz": None}
    min_corner = wrapper.grid.x_min
    max_corner = wrapper.grid.x_max
    xy_extent = [min_corner[0], max_corner[0],
                 min_corner[1], max_corner[1]]

    ax = plt.gca()
    if not target_plt is None:
        ax.add_patch(target_plt)
    try:
        state[2] = radians(state[2])
        _, _, yaw, v = wrapper.grid.index(state)

        times["ttr"] = time.time()
        ttr = wrapper.min_ttr(state)
        times["ttr"] = time.time() - times["ttr"]

        times["set"] = time.time()
        curr_set = wrapper.reach_at_t(ttr)
        times["set"] = time.time() - times["set"]

        times["grad"] = time.time()
        grad_yaw = wrapper.gradient(state, ttr, 2)
        grad_v = wrapper.gradient(state, ttr, 3)
        times["grad"] = time.time() - times["grad"]

        times["viz"] = time.time()
        min_corner = wrapper.grid.x_min
        max_corner = wrapper.grid.x_max
        xy_extent = [min_corner[0], max_corner[0],
                     max_corner[1], min_corner[1]]
        plt.plot(state[0], state[1], 'ro')
        annotate_str = f'TTR: {ttr:.2f} [s], Grad: ({grad_yaw:.3f}, {grad_v:.3f})'
        plt.annotate(annotate_str,
                     (state[0]+0.1, state[1]+0.1),
                     color="gray")
        set_sliced = curr_set[:, :, yaw, v]
        pylevel.utilities.visualize_XY(wrapper, set_sliced,
                                       ttr, show=show, cmap="Purples", alpha = 0.1,
                                       extent=xy_extent)
        times["viz"] = time.time() - times["viz"]
        times["total_timed"] = sum(times.values())
    except (pylevel.error.IndexNotInGridError,
            pylevel.error.StateNotReachableError) as e:
        plt.title("Not in Backward Reach Set")
        plt.xlabel("x [m]")
        plt.ylabel("y [m]")
        plt.xlim(xy_extent[:2])
        plt.ylim(xy_extent[2:])
        ax.set_aspect('equal')
        if show:
            plt.show()

    times["func_call"] = time.time() - tic
    if show_timing:
        for (key, value) in times.items():
            if not value is None:
                times[key] = str(np.around(value*1000, 2)) + " ms"
        print(times)


def animate_reachset_evolution(wrapper, viz_heading, viz_vel, target_plt=None):
    """Applicaiton-specific, viz_heading in degrees, viz_vel in m/s"""
    t_idx = list(wrapper.time)
    state_idx = wrapper.grid.index_valid(np.array([0, 0,
                                                   radians(viz_heading),
                                                   viz_vel]))
    heading_idx = state_idx[2]
    velocity_idx = state_idx[3]
    min_corner = wrapper.grid.x_min
    max_corner = wrapper.grid.x_max
    xy_extent = [min_corner[0], max_corner[0],
                 max_corner[1], min_corner[1]]

    reachable_states = [wrapper.reach_at_t(t) for t in t_idx[:-1]]
    ax = plt.gca()
    if not target_plt is None:
        ax.add_patch(target_plt)
    for reachable_states, t in zip(reachable_states,t_idx[:-1]):
        states_sliced = reachable_states[:, :, heading_idx, velocity_idx]
        pylevel.utilities.visualize_XY(wrapper, states_sliced,
                                       t, show=False, cmap="Purples", alpha = 0.1,
                                       extent=xy_extent)
        pylevel.utilities.show_plots_for_time(time_in_seconds=.3)

    pylevel.utilities.show_plots()
