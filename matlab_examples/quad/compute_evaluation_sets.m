% Example script for computing RS for evaluation sets
clear

%% Grouping directory of generated state sets
save_path = store_under('eval');
% % Show available videowriters
% VideoWriter.getProfiles()

%% General Parameters 
% Acceleration limits
default_params.uMin = -1;
default_params.uMax = 1;
% Define computation accuracy
default_params.accuracy = 'low';
% Define sampling time
default_params.dt = .1;
% By default consider zero disturbance, but in avoid situations consider
% disturbance to \dot[x, v_x, y, v_y]
default_params.dMax = [0.0, 0.0, 0.0, 0.0]; 
% Worst-case disturbance
dWorstCase = 0.75;
default_params.makeVideo = false;

% Define grid resolution [x, v_x, y, v_y]
% Note, these resolutions should be smaller than the target region
resolution_low = [0.1 0.1 0.1 0.1];
resolution_medium = [0.05 0.05 0.05 0.05];
resolution_high =  [0.025 0.05 0.025 0.05];

% Define state space domain as box constraint
grid_min = [-1.5, -0.25, -1.5, -0.25];
grid_max = [1.5, 0.25, 1.5, 0.25];

grid = create_grid_from_resolution(grid_min, grid_max, resolution_low);

%% Forward Reachable Tube - Test parameters
params = default_params;
% Label reachable dataset
% Time horizon
params.T = 2.0;
% Define as forwards reachable computation
params.isBackwards = false;
params.figNum = 1;
% Set colouring to be reach and not avoid
params.is_reach_colors = true;
% To be defined
params.isTube = true;
% TODO: debug video creation -> On Ubuntu no MPEG-4 codec
% params.videoFilename = [save_path 'reach_BRS'];

% %% FRS: Low - Res
% % Define grid for computation
% params.label = 'frs_low_resolution_low_horizon';
% params.g = create_grid_from_resolution(grid_min, grid_max, resolution_low);
% % Define target set with (grid, ignoreDims, center, radius)
% params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
% data = quad_RS(params);
% % (unsupported for compound types) export_to_hdf5(save_path, params.label,  data);
% % % (optional) export to mat
% export_to_mat(save_path, params.label,  data);
% 
% %% FRS: Low - Medium Horizon
% % Define grid for computation
% params.label = 'frs_low_resolution_medium_horizon';
% params.g = create_grid_from_resolution(grid_min, grid_max, resolution_low);
% % Time horizon
% params.T = 3.0;
% % Define target set with (grid, ignoreDims, center, radius)
% params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
% data = quad_RS(params);
% % (unsupported for compound types) export_to_hdf5(save_path, params.label,  data);
% % % (optional) export to mat
% export_to_mat(save_path, params.label,  data);
% 
% %% FRS: Low - Long Horizon
% % Define grid for computation
% params.label = 'frs_low_resolution_medium_horizon';
% params.g = create_grid_from_resolution(grid_min, grid_max, resolution_low);
% % Time horizon
% params.T = 5.0;
% % Define target set with (grid, ignoreDims, center, radius)
% params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
% data = quad_RS(params);
% % (unsupported for compound types) export_to_hdf5(save_path, params.label,  data);
% % % (optional) export to mat
% export_to_mat(save_path, params.label,  data);

%% FRS: Medium - Res
% Define grid for computation
params.label = 'frs_medium_resolution_medium_horizon';
params.g = create_grid_from_resolution(grid_min, grid_max, resolution_medium);
% Define target set with (grid, ignoreDims, center, radius)
params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);
% % (unsupported for compound types) export_to_hdf5(save_path, params.label,  data);

% %% FRS: High - Res
% % Define grid for computation
% params.label = 'frs_high_resolution_low_horizon';
% params.g = create_grid_from_resolution(grid_min, grid_max, resolution_high);
% % Define target set with (grid, ignoreDims, center, radius)
% params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
% data = quad_RS(params);
% export_to_mat(save_path, params.label,  data);