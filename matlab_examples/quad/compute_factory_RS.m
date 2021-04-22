% Example script for computing RS for factory example
clear

%% Grouping directory of generated state sets
label = 'drone';
path = fileparts(mfilename('fullpath'));
save_path = [path  '/../../resources/generated/' label];
fprintf("Storing reachable data under %s", save_path);

%% General Parameters 
default_params.uMin = -1; % Acceleration limits
default_params.uMax = 1;
% by default consider zero disturbance, but in avoid situations consider
% worst-case
default_params.dMax = [0.0, 0.0, 0.0, 0.0]; % disturbance to \dot[x, v_x, y, v_y]
dWorstCase = 0.75; % worst-case disturbance

default_params.makeVideo = false;

% Desired resolution of grid [x, v_x, y, v_y]
global_resolution = [0.1 0.1 0.1 0.1];
zone_resolution = [0.05 0.05 0.05 0.05];
% Note, these resolutions should be smaller than the target region

% Define factory global grid
global_min = [-1.5, -0.25, -1.5, -0.25];
global_max = [1.5, 0.25, 1.5, 0.25];
global_N = N_from_resolution(global_min, global_max, global_resolution);
global_g = createGrid(global_min, global_max, global_N);

% Inspect Zone A
inspect_zone_a_min = [0.0, -0.25, 0.0, -0.25];
inspect_zone_a_max = [1.5, 0.25, 1.5, 0.25];
inspect_zone_a_N = N_from_resolution(inspect_zone_a_min, inspect_zone_a_max, zone_resolution);
inspect_zone_a_g = createGrid(inspect_zone_a_min, inspect_zone_a_max, inspect_zone_a_N);

% Inspect Zone B
inspect_zone_b_min = [0.0, -0.25, -1.5, -0.25];
inspect_zone_b_max = [1.5, 0.25, 0.0, 0.25];
inspect_zone_b_N = N_from_resolution(inspect_zone_b_min, inspect_zone_b_max, zone_resolution);
inspect_zone_b_g = createGrid(inspect_zone_b_min, inspect_zone_b_max, inspect_zone_b_N);

% Create shelf obstacles (including over approx. of minkowski sum)
shelf_w = 0.32 + 0.15*2;
shelf_l = 1.44 + 0.15*2;
shelf_center_center = [0.5 0]; % xy position of center of shelf
shelf_center_min = shelf_center_center - [shelf_l/2 shelf_w/2];
shelf_center_max = shelf_center_center + [shelf_l/2 shelf_w/2];
shelf_right_center = [0 -1.5];
shelf_right_min = shelf_right_center - [shelf_w/2 shelf_l/2];
shelf_right_max = shelf_right_center + [shelf_w/2 shelf_l/2];
shelf_left_center = [0 1.5]; % xy position of center of shelf
shelf_left_min = shelf_left_center - [shelf_w/2 shelf_l/2];
shelf_left_max = shelf_left_center + [shelf_w/2 shelf_l/2];

% Embed shelves into global grid
min_center = [shelf_center_min(1), -Inf, shelf_center_min(2), -Inf];
max_center = [Inf, Inf, shelf_center_max(2), Inf];
shelf_center = shapeRectangleByCorners(global_g, min_center, max_center);
min_right = [shelf_right_min(1), -Inf, -Inf, -Inf];
max_right = [shelf_right_max(1), Inf, shelf_right_max(2), Inf];
shelf_right = shapeRectangleByCorners(global_g, min_right, max_right);
min_left = [shelf_left_min(1), -Inf, shelf_left_min(2), -Inf];
max_left = [shelf_left_max(1), Inf, Inf, Inf];
shelf_left = shapeRectangleByCorners(global_g, min_left, max_left);
shelves_global = min(min(shelf_center, shelf_right), shelf_left);

% Embed shelves into Inspect Zone A
min_center = [-Inf, -Inf, -Inf, -Inf];
max_center = [shelf_center_max(1), Inf, shelf_center_max(2), Inf];
shelf_center = shapeRectangleByCorners(inspect_zone_a_g, min_center, max_center);
min_left = [-Inf, -Inf, shelf_left_min(2), -Inf];
max_left = [shelf_left_max(1), Inf, Inf, Inf];
shelf_left = shapeRectangleByCorners(inspect_zone_a_g, min_left, max_left);
shelves_inspect_a = min(shelf_center, shelf_left);

% Embed shelves into Inspect Zone B
min_center = [shelf_center_min(1), -Inf, shelf_center_min(2), -Inf];
max_center = [Inf, Inf, Inf, Inf];
shelf_center = shapeRectangleByCorners(inspect_zone_b_g, min_center, max_center);
min_right = [-Inf, -Inf, -Inf, -Inf];
max_right = [shelf_right_max(1), Inf, shelf_right_max(2), Inf];
shelf_right = shapeRectangleByCorners(inspect_zone_b_g, min_right, max_right);
shelves_inspect_b = min(shelf_center, shelf_right);

%% Forward Reachable Tube
params = default_params;
params.isBackwards = false; % FRT
params.g = global_g;

params.figNum = 1;
params.T = 7.0; % seconds
params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
params.is_reach_colors = true;
params.isTube = true;
params.label = 'FRS';
params.videoFilename = [save_path 'reach_BRS'];
[~, FRS_data, FRS_time] = quad_RS(params);

g = global_g;
data_save_path = [save_path 'FRS'];

%% Backward Reachable Tubes Inspect A
% Compute backward reach tubes for TLT corresponding to LTL statement:
% (Eventually-Always in Inspection Zone Until Eventually Inspection Goal)
% and (Always not Shelf)

% Compute avoid leave inspection zone (RCIS of inspection zone)
params = default_params;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 2;
params.isBackwards = true; % BRS
params.g = inspect_zone_a_g;
params.T = 2;
params.is_avoid = true;
params.is_boundary_avoid = true;
params.is_avoid_colors = true;
params.isTube = true;
params.label = 'always_inspection_zone_a_BRS';
params.videoFilename = [save_path 'always_inspection_zone_a_BRS'];
[~, alw_inspect_zone_a_data, alw_inspect_zone_a_time] = quad_RS(params);
% define complement as the RCIS
rcis_inspect_zone_a = -alw_inspect_zone_a_data(:, :, :, :, end);

% Compute reach inspection goal in inspection zone
params = default_params;
params.figNum = 2;
params.isBackwards = true; % BRS
params.g = inspect_zone_a_g;
params.T = 5; % seconds
params.target = shapeCylinder(params.g, [2, 4], [1.1; 0; 0.5; 0], 0.1);
params.obstacle = min(-rcis_inspect_zone_a, shelves_inspect_a);
params.is_reach_colors = true;
params.isTube = false;
params.label = 'eventually_inspection_goal_a_BRS';
params.videoFilename = [save_path params.label];
[~, ev_inspect_goal_a_data, ev_inspect_goal_a_time] = quad_RS(params);

% Compute reach RCIS of inspection zone
params = default_params;
params.figNum = 2;
params.isBackwards = true; % BRS
params.g = global_g;
params.T = 12;
rcis_inspect_zone_a_global = migrateGrid(inspect_zone_a_g, rcis_inspect_zone_a, global_g');
params.target = rcis_inspect_zone_a_global;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.label = 'eventually_rcis_inspection_a_BRS';
params.videoFilename = [save_path 'eventually_rcis_inspection_a_BRS'];
[~, ev_rcis_inspect_zone_a_data, ev_rcis_inspect_zone_a_time] = quad_RS(params);

%% Backward Reachable Tubes Inspect B
% Compute backward reach tubes for TLT corresponding to LTL statement:
% (Eventually-Always in Inspection Zone Until Eventually Inspection Goal)
% and (Always not Shelf)

% Compute avoid leave inspection zone (RCIS of inspection zone)
params = default_params;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 3;
params.isBackwards = true; % BRS
params.g = inspect_zone_b_g;
params.T = 2;
params.is_avoid = true;
params.is_boundary_avoid = true;
params.is_avoid_colors = true;
params.isTube = true;
params.label = 'eventually_inspection_goal_a_BRS';
params.videoFilename = [save_path 'always_inspection_zone_b_BRS'];
[~, alw_inspect_zone_b_data, alw_inspect_zone_b_time] = quad_RS(params);
% define complement as the RCIS
rcis_inspect_zone_b = -alw_inspect_zone_b_data(:, :, :, :, end);

% Compute reach inspection goal in inspection zone
params = default_params;
params.figNum = 3;
params.isBackwards = true; % BRS
params.g = inspect_zone_b_g;
params.T = 8; % seconds
params.target = shapeCylinder(params.g, [2, 4], [1.1; 0; -0.5; 0], 0.1);
params.obstacle = min(-rcis_inspect_zone_b, shelves_inspect_b);
params.is_reach_colors = true;
params.isTube = false;
params.label = 'eventually_inspection_goal_a_BRS';
params.videoFilename = [save_path 'eventually_inspection_goal_b_BRS'];
[~, ev_inspect_goal_b_data, ev_inspect_goal_b_time] = quad_RS(params);

% Compute reach RCIS of inspection zone
params = default_params;
params.figNum = 3;
params.isBackwards = true; % BRS
params.g = global_g;
params.T = 12;
rcis_inspect_zone_b_global = migrateGrid(inspect_zone_b_g, rcis_inspect_zone_b, global_g');
params.target = rcis_inspect_zone_b_global;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.label = 'eventually_rcis_inspection_b_BRS';
params.videoFilename = [save_path 'eventually_rcis_inspection_b_BRS'];
[~, ev_rcis_inspect_zone_b_data, ev_rcis_inspect_zone_b_time] = quad_RS(params);

%% Avoid Backward Reachable Tubes of Shelves
% Compute avoid shelf in each grid
params = default_params;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 4;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.g = inspect_zone_a_g;
params.T = 2;
params.target = shelves_inspect_a;
params.is_avoid_colors = true;
params.isTube = true;
params.label = 'always_no_shelf_inspect_zone_a_BRS';
params.videoFilename = [save_path 'always_no_shelf_inspect_zone_a_BRS'];
[~, alw_no_shelf_inspect_zone_a_data, alw_no_shelf_inspect_zone_a_time] = quad_RS(params);

% Compute avoid shelf in inspect zone A grid
params = default_params;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 5;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.g = inspect_zone_b_g;
params.T = 2;
params.target = shelves_inspect_b;
params.is_avoid_colors = true;
params.isTube = true;
params.label = 'always_no_shelf_inspect_zone_b_BRS';
params.videoFilename = [save_path 'always_no_shelf_inspect_zone_b_BRS'];
[~, alw_no_shelf_inspect_zone_b_data, alw_no_shelf_inspect_zone_b_time] = quad_RS(params);

% Compute avoid shelf in inspect zone A grid
params = default_params;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 6;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.g = global_g;
params.T = 2;
params.target = shelves_global;
params.is_avoid_colors = true;
params.isTube = true;
params.label = 'always_no_shelf_global_BRS';
params.videoFilename = [save_path 'always_no_shelf_global_BRS'];
[~, alw_no_shelf_global_data, alw_no_shelf_global_time] = quad_RS(params);

%% Save RS and other useful data
% generic FRS
g = global_g;
data_save_path = [save_path 'FRS'];
save(data_save_path, 'g', 'FRS_data', 'FRS_time');

% BRS for reaching inspect zone RCIS
g = global_g;
data_save_path = [save_path 'ev_rcis_inspect_zone_a'];
save(data_save_path, 'g', 'ev_rcis_inspect_zone_a_data', 'ev_rcis_inspect_zone_a_time');
% BRS for always staying inside RCIS
g = inspect_zone_a_g;
data_save_path = [save_path 'alw_inspect_zone_a'];
save(data_save_path, 'g', 'alw_inspect_zone_a_data', 'alw_inspect_zone_a_time');
% BRS for reaching inspect goal
g = inspect_zone_a_g;
data_save_path = [save_path 'ev_inspect_goal_a'];
save(data_save_path, 'g', 'ev_inspect_goal_a_data', 'ev_inspect_goal_a_time');

% BRS for reaching inspect zone RCIS
g = global_g;
data_save_path = [save_path 'ev_rcis_inspect_zone_b'];
save(data_save_path, 'g', 'ev_rcis_inspect_zone_b_data', 'ev_rcis_inspect_zone_b_time');
% BRS for always staying inside RCIS
g = inspect_zone_b_g;
data_save_path = [save_path 'alw_inspect_zone_b'];
save(data_save_path, 'g', 'alw_inspect_zone_b_data', 'alw_inspect_zone_b_time');
% BRS for reaching inspect goal
g = inspect_zone_b_g;
data_save_path = [save_path 'ev_inspect_goal_b'];
save(data_save_path, 'g', 'ev_inspect_goal_b_data', 'ev_inspect_goal_b_time');

% BRS for always avoiding shelf in inspect zone
g = inspect_zone_a_g;
data_save_path = [save_path 'alw_no_shelf_inspect_zone_a'];
save(data_save_path, 'g', 'alw_no_shelf_inspect_zone_a_data', 'alw_no_shelf_inspect_zone_a_time');
g = inspect_zone_b_g;
data_save_path = [save_path 'alw_no_shelf_inspect_zone_b'];
save(data_save_path, 'g', 'alw_no_shelf_inspect_zone_b_data', 'alw_no_shelf_inspect_zone_b_time');

% BRS for always avoiding shelf in global grid
g = global_g;
data_save_path = [save_path 'alw_no_shelf_global'];
save(data_save_path, 'g', 'alw_no_shelf_global_data', 'alw_no_shelf_global_time');
