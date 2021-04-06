% Example script for computing RS for SVEA
clear

%% General Parameters
save_path = '/home/fjiang/Projects/MATLAB/Experiments/SML_level_set/cached_rs/svea/';
params.sMax = pi/5; % Steering limit (assumed symmetric)
params.aMax = 1.5; % Max accel
params.aMin = -1.0; % Min accel, good to be conservative for safer braking
params.isBackwards = true; % BRS or FRS (FRS requires more parameter changes below)
params.makeVideo = true;

% Desired resolution of grid [x, y, theta, v]
resolution = [0.05 0.05 pi/20 0.1];
% Note, these resolutions should be smaller than the target regions

% Create grid
max_v = 1.5;
g_min = [-3, -2, -pi, -max_v];
g_max = [1.5, 2, pi, max_v];
g_N = N_from_resolution(g_min, g_max, resolution);
g = createGrid(g_min, g_max, g_N, 3);

%% Backward Reachable Set
params.figNum = 1;
params.T = 5; % time horizon
params.g = g;
params.target = shapeCylinder(g, [3, 4], [0; 0; 0; 0], 0.2);
params.is_reach_colors = true;
params.stop_converge = true;
params.isTube = false;
params.videoFilename = [save_path 'reach_BRS'];
[~, val_data, time_vec] = svea_RS(params);

%% Save RS and other useful data

% Save full reachable set solution
data_save_path = [save_path 'RS'];
save(data_save_path, 'g', 'val_data', 'time_vec');

% Save just min time-to-reach, and gradients needed for control
[TTR, grad_theta, grad_v] = extract_useful(g, val_data, time_vec);
data_save_path = [save_path 'TTR_and_grad'];
save(data_save_path, 'g', 'TTR', 'grad_theta', 'grad_v')
