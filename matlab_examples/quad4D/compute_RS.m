% Example script for computing RS for a double integrator
clear

%% General Parameters
save_path = '/home/fjiang/Projects/MATLAB/Experiments/SML_level_set/cached_rs/quad4D/';
params.uMin = -1; % Acceleration limits
params.uMax = 1;
params.makeVideo = false;

% Desired resolution of grid [x, v_x, y, v_y]
resolution = [0.02 0.1 0.02 0.1];
% Note, these resolutions should be smaller than the target region

% Create grid
g_min = [-1, -1, -1, -1];
g_max = [1, 1, 1, 1];
g_N = N_from_resolution(g_min, g_max, resolution);
g = createGrid(g_min, g_max, g_N);
params.g = g;

%% Forward Reachable Set
params.isBackwards = false; % FRS

params.figNum = 1;
params.T = 1; % seconds
params.target = shapeCylinder(g, [2, 4], [0; 0; 0; 0], 0.1);
params.isTube = true;
params.videoFilename = [save_path 'reach_BRS'];
[~, FRS_data, FRS_time] = quad4D_RS(params);

%% Backward Reachable Set
params.isBackwards = true; % BRS

params.figNum = 2;
params.T = 1; % seconds
params.target = shapeCylinder(g, [2, 4], [0; 0; 0; 0], 0.05);
params.is_reach_colors = true;
params.videoFilename = [save_path 'reach_BRS'];
[~, BRS_data, BRS_time] = quad4D_RS(params);

%% Save RS and other useful data

% Save full reachable set solution
data_save_path = [save_path 'FRS'];
save(data_save_path, 'g', 'FRS_data', 'FRS_time');

data_save_path = [save_path 'BRS'];
save(data_save_path, 'g', 'BRS_data', 'BRS_time');