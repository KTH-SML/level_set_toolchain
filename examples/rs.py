#!/usr/bin/env python

"""
Examples of working with value function solutions to the HJI inequality
over time, and with a value function that has been optimized across time
already. quad4D BRS is a backward reach set, SVEA TTR is the set of
minimum time to reach an avoid set.
"""

import os
from scipy.io import loadmat
from grid import GridData

path = os.path.dirname(os.path.abspath(__file__))
# for RS example
quad_BRS_file = path + "/../resources/quad4D/low_res_BRS.mat"
# for TTR and grad example
svea_file = path + "/../resources/svea/TTR_and_grad.mat"

def main():
    # load from MATLAB files
    print('# Loading for MATLAB files')
    quad_BRS_data = loadmat(quad_BRS_file)
    svea_data = loadmat(svea_file)

    print('# Building Reachable Sets')
    # RS solutions over time for quadrotor in 2D plane
    BRS_grid = quad_BRS_data['g']
    BRS_val_funcs = quad_BRS_data['BRS_data'] # one valfunc per time step
    BRS_times = quad_BRS_data['BRS_time'].tolist()[0]
    BRS_list = []
    sublevel_idx = []
    for i in range(len(BRS_times)):
        BRS = GridData(BRS_grid, BRS_val_funcs[:, :, :, :, i])
        BRS_list.append(BRS)
        # 1 - in sublevel set, 0 - not in sublevel set
        sublevel_idx.append(BRS.sublevel_set_idx(level=0.0))

    # min Time-to-Reach (TTR) value func. for SVEA
    TTR_grid = svea_data['g']
    TTR_val_func = svea_data['TTR']
    TTR_val_func[TTR_val_func == 1000000.0] = float('inf')
    TTR = GridData(TTR_grid, TTR_val_func)

    # Access value function with get_raw_value() or get_interp_value()
    # e.g. TTR.get_interp_value(state)

if __name__ == '__main__':
    main()
