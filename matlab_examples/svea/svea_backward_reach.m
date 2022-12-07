% Example script for computing RS for SVEA
clear

%% General Parameters
save_path = store_under('svea');
params.sMax = pi/5; % Steering limit (assumed symmetric)
params.aMax = 1; % Max accel
params.aMin = -1; % Min accel, good to be conservative for safer braking
params.isBackwards = true;
params.makeVideo = false;
% video recording only works on Windows or MacOS
% alternatively remove 'MPEG-4' in VideoWriter(extraArgs.videoFilename,'MPEG-4')
% in HJIPDE_solve in helperOC

% Desired resolution of grid [x, y, theta, v]
resolution = [0.2 0.2 pi/10 0.1];
% Note, these resolutions should be smaller than the target regions

% Create grid
max_v = 1;
g_min = [-3, -2, -pi, -max_v];
g_max = [3, 2, pi, max_v];
g_N = N_from_resolution(g_min, g_max, resolution);
g = createGrid(g_min, g_max, g_N, 3);

%% Backward Reachable Set
params.figNum = 1;
params.T = 2; % time horizon
params.g = g;
params.target = shapeCylinder(g, [3, 4], [0; 0; 0; 0], 0.5);
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path 'svea_reach'];
reach_data = svea_RS(params);

%% Save RS
export_to_mat(save_path, 'svea_reach', reach_data);