% Example script for computing RS for factory example
clear

%% General Parameters
save_path = '/home/fjiang/Projects/MATLAB/Experiments/SML_level_set/resources/quad4D/factory/';
default_params.uMin = -2; % Acceleration limits
default_params.uMax = 2;
default_params.makeVideo = false;

% Desired resolution of grid [x, v_x, y, v_y]
resolution = [0.1 0.1 0.1 0.1];
% Note, these resolutions should be smaller than the target region

% Define factory global grid
global_min = [-1.5, -0.25, -1.5, -0.25];
global_max = [1.5, 0.25, 1.5, 0.25];
global_N = N_from_resolution(global_min, global_max, resolution);
global_g = createGrid(global_min, global_max, global_N);

% Define inspection zone grid
inspect_zone_min = [0.0, -0.25, -1.5, -0.25];
inspect_zone_max = [1.5, 0.25, -0.0, 0.25];
inspect_zone_N = N_from_resolution(inspect_zone_min, inspect_zone_max, resolution);
inspect_zone_g = createGrid(inspect_zone_min, inspect_zone_max, inspect_zone_N);

% Create shelf obstacles
shelf_w = 0.32;
shelf_l = 1.44;
x_align_shelf_center = [0.5 0]; % xy position of center of shelf
y_align_shelf_center = [0 -1.5];
shelf1_min = x_align_shelf_center - [shelf_l/2 shelf_w/2];
shelf1_max = x_align_shelf_center + [shelf_l/2 shelf_w/2];
shelf2_min = y_align_shelf_center - [shelf_w/2 shelf_l/2];
shelf2_max = y_align_shelf_center + [shelf_w/2 shelf_l/2];

min1 = [shelf1_min(1), -Inf, shelf1_min(2), -Inf];
max1 = [Inf, Inf, shelf1_max(2), Inf];
min2 = [shelf2_min(1), -Inf, -Inf, -Inf];
max2 = [shelf2_max(1), Inf, shelf2_max(2), Inf];
shelf1 = shapeRectangleByCorners(global_g, min1, max1);
shelf2 = shapeRectangleByCorners(global_g, min2, max2);
shelves_global = min(shelf1, shelf2);

min1 = [shelf1_min(1), -Inf, shelf1_min(2), -Inf];
max1 = [Inf, Inf, Inf, Inf];
min2 = [-Inf, -Inf, -Inf, -Inf];
max2 = [shelf2_max(1), Inf, shelf2_max(2), Inf];
shelf1 = shapeRectangleByCorners(inspect_zone_g, min1, max1);
shelf2 = shapeRectangleByCorners(inspect_zone_g, min2, max2);
shelves_inspect_zone = min(shelf1, shelf2);
                 
%% Forward Reachable Tube
params = default_params;
params.isBackwards = false; % FRT
params.g = global_g;

params.figNum = 1;
params.T = 4.0; % seconds
params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
params.is_reach_colors = true;
params.isTube = true;
params.videoFilename = [save_path 'reach_BRS'];
[~, FRS_data, FRS_time] = quad4D_RS(params);

%% Backward Reachable Tubes
% Compute backward reach tubes for TLT corresponding to LTL statement:
% (Eventually-Always in Inspection Zone Until Eventually Inspection Goal)
% and (Always not Shelf)

% Compute avoid leave inspection zone (RCIS of inspection zone)
params = default_params;
params.figNum = 2;
params.isBackwards = true; % BRS
params.g = inspect_zone_g;
params.T = 1;
params.is_boundary_avoid = true;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path 'always_inspection_zone_BRS'];
[~, alw_inspect_zone_data, alw_inspect_zone_time] = quad4D_RS(params);
% define complement as the RCIS
rcis_inspect_zone = -alw_inspect_zone_data(:, :, :, :, end);

% Compute reach inspection goal in inspection zone
params = default_params;
params.figNum = 3;
params.isBackwards = true; % BRS
params.g = inspect_zone_g;
params.T = 8; % seconds
params.target = shapeCylinder(params.g, [2, 4], [1.1; 0; -0.5; 0], 0.1);
params.obstacle = min(-rcis_inspect_zone, shelves_inspect_zone);
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path 'eventually_inspection_goal_BRS'];
[~, ev_inspect_goal_data, ev_inspect_goal_time] = quad4D_RS(params);

% Compute reach RCIS of inspection zone
params = default_params;
params.figNum = 4;
params.isBackwards = true; % BRS
params.g = global_g;
params.T = 12;
rcis_inspect_zone_global = migrateGrid(inspect_zone_g, rcis_inspect_zone, global_g');
params.target = rcis_inspect_zone_global;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path 'eventually_rcis_inspection_BRS'];
[~, ev_rcis_inspect_zone_data, ev_rcis_inspect_zone_time] = quad4D_RS(params);

% Compute avoid shelf in each grid
params = default_params;
params.figNum = 5;
params.isBackwards = true; % BRS
params.g = inspect_zone_g;
params.T = 1;
params.obstacle = shelves_inspect_zone;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path 'always_no_shelf_inspect_zone_BRS'];
[~, alw_no_shelf_inspect_zone_data, alw_no_shelf_inspect_zone_time] = quad4D_RS(params);
params.figNum = 6;
params.isBackwards = true; % BRS
params.g = global_g;
params.T = 1;
params.obstacle = shelves_global;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path 'always_no_shelf_global_BRS'];
[~, alw_no_shelf_global_data, alw_no_shelf_global_time] = quad4D_RS(params);


%% Save RS and other useful data
% generic FRS
g = global_g;
data_save_path = [save_path 'FRS'];
save(data_save_path, 'g', 'FRS_data', 'FRS_time');

% BRS for reaching inspect zone RCIS
g = global_g;
data_save_path = [save_path 'ev_rcis_inspect_zone'];
save(data_save_path, 'g', 'ev_rcis_inspect_zone_data', 'ev_rcis_inspect_zone_time');

% BRS for always staying inside RCIS
g = inspect_zone_g;
data_save_path = [save_path 'alw_inspect_zone'];
save(data_save_path, 'g', 'alw_inspect_zone_data', 'alw_inspect_zone_time');

% BRS for reaching inspect goal
g = inspect_zone_g;
data_save_path = [save_path 'ev_inspect_goal'];
save(data_save_path, 'g', 'ev_inspect_goal_data', 'ev_inspect_goal_time');

% BRS for always avoiding shelf in inspect zone
g = inspect_zone_g;
data_save_path = [save_path 'alw_no_shelf_inspect_zone'];
save(data_save_path, 'g', 'alw_no_shelf_inspect_zone_data', 'alw_no_shelf_inspect_zone_time');

% BRS for always avoiding shelf in global grid
g = global_g;
data_save_path = [save_path 'alw_no_shelf_global'];
save(data_save_path, 'g', 'alw_no_shelf_global_data', 'alw_no_shelf_global_time');
