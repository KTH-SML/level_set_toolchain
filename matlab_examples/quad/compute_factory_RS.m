% Example script for computing RS for factory example
clear

%% Grouping directory of generated state sets
save_path = store_under('drone');

%% General Parameters 
default_params.uMin = -1; % Acceleration limits
default_params.uMax = 1;
% Define computation accuracy
default_params.accuracy = 'low';
% Define sampling time
default_params.dt = .1;
% by default consider zero disturbance, but in avoid situations consider
% worst-case
% disturbance to \dot[x, v_x, y, v_y]
default_params.dMax = [0.0, 0.0, 0.0, 0.0]; 
% worst-case disturbance
dWorstCase = 0.75; 
default_params.makeVideo = false;

%% Define Grids
% Desired resolution of grid [x, v_x, y, v_y]
% Note, these resolutions should be smaller than the target region
resolution_global = [0.1 0.05 0.1 0.05];
resolution_zone = [0.1 0.05 0.1 0.05];

% Define factory global grid
min_global = [-1.5, -0.25, -1.5, -0.25];
max_global = [1.5, 0.25, 1.5, 0.25];

% Inspect Zone A
min_zone_a = [0.0, -0.25, 0.0, -0.25];
max_zone_a = [1.5, 0.25, 1.5, 0.25];

% Inspect Zone B
min_zone_b = [0.0, -0.25, -1.5, -0.25];
max_zone_b = [1.5, 0.25, 0.0, 0.25];

%% Define Obstacles
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

%% State Sets of Inspect Zone A Grid: 
% Backward Reachable Tubes Inspect A
% Compute backward reach tubes for TLT corresponding to LTL statement:
% (Eventually-Always in Inspection Zone Until Eventually Inspection Goal)
% and (Always not Shelf)
grid = create_grid_from_resolution(min_zone_a, max_zone_a, resolution_zone);
% Reuse grid to migrate RCIS to global grid
grid_zone_a = grid;

% Embed shelves into Inspect Zone A
min_center = [-Inf, -Inf, -Inf, -Inf];
max_center = [shelf_center_max(1), Inf, shelf_center_max(2), Inf];
shelf_center = shapeRectangleByCorners(grid, min_center, max_center);
min_left = [-Inf, -Inf, shelf_left_min(2), -Inf];
max_left = [shelf_left_max(1), Inf, Inf, Inf];
shelf_left = shapeRectangleByCorners(grid, min_left, max_left);
shelves_inspect_a = min(shelf_center, shelf_left);

%% Compute avoid leave inspection zone (RCIS of inspection zone)
params = default_params;
params.label = 'alw_inspect_zone_a';
params.g = grid;
% assume almost worst case
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; 
params.figNum = 2;
params.isBackwards = true; % BRS
params.T = 2;
params.is_avoid = true;
params.is_boundary_avoid = true;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
% Define target set with (grid, ignoreDims, center, radius)
export_to_mat(save_path, params.label,  data);
% Reuse in global grid for eventually inspection zone
rcis_inspect_zone_a =  -data.value_function(:, :, :, :, end);;

% Compute reach inspection goal in inspection zone
params = default_params;
params.label = 'ev_inspect_goal_a';
params.g = grid;
params.figNum = 2;
params.isBackwards = true; % BRS
params.T = 12; % seconds
params.target = shapeCylinder(params.g, [2, 4], [1.1; 0; 0.5; 0], 0.1);
params.obstacle = min(-rcis_inspect_zone_a, shelves_inspect_a);
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);

% Inspect Zone A Grid: Avoid Backward Reachable Tubes of Shelves
% Compute avoid shelf in each grid
params = default_params;
params.label = 'alw_no_shelf_inspect_zone_a';
params.g = grid;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 4;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.T = 2;
params.target = shelves_inspect_a;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);

%% State Sets of Inspect Zone B Grid: 
% Backward Reachable Tubes Inspect B
% Compute backward reach tubes for TLT corresponding to LTL statement:
% (Eventually-Always in Inspection Zone Until Eventually Inspection Goal)
% and (Always not Shelf)

grid = create_grid_from_resolution(min_zone_b, max_zone_b, resolution_zone);
% Reuse grid to migrate RCIS to global grid
grid_zone_b = grid;

% Embed shelves into Inspect Zone B
min_center = [shelf_center_min(1), -Inf, shelf_center_min(2), -Inf];
max_center = [Inf, Inf, Inf, Inf];
shelf_center = shapeRectangleByCorners(grid, min_center, max_center);
min_right = [-Inf, -Inf, -Inf, -Inf];
max_right = [shelf_right_max(1), Inf, shelf_right_max(2), Inf];
shelf_right = shapeRectangleByCorners(grid, min_right, max_right);
shelves_inspect_b = min(shelf_center, shelf_right);

% Compute avoid leave inspection zone (RCIS of inspection zone)
params = default_params;
params.label = 'alw_inspect_zone_b';
params.g = grid;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 3;
params.isBackwards = true; % BRS
params.T = 2;
params.is_avoid = true;
params.is_boundary_avoid = true;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);
% Reuse in global grid for eventually inspection zone
rcis_inspect_zone_b =  - data.value_function(:, :, :, :, end);

% Compute reach inspection goal in inspection zone
params = default_params;
params.label = 'ev_inspect_goal_b';
params.g = grid;
params.figNum = 3;
params.isBackwards = true; % BRS
params.T = 12; % seconds
params.target = shapeCylinder(params.g, [2, 4], [1.1; 0; -0.5; 0], 0.1);
params.obstacle = min(-rcis_inspect_zone_b, shelves_inspect_b);
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path params.label];
data= quad_RS(params);
export_to_mat(save_path, params.label,  data);

% Compute avoid shelf in inspect zone B grid
params = default_params;
params.label = 'alw_no_shelf_inspect_zone_b';
params.g = grid;
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; % assume almost worst case
params.figNum = 5;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.T = 2;
params.target = shelves_inspect_b;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);

%% State Sets of Global Grid: 
% Forward Reachable Tube
grid = create_grid_from_resolution(min_global, max_global, resolution_global);

% Embed shelves into global grid
min_center = [shelf_center_min(1), -Inf, shelf_center_min(2), -Inf];
max_center = [Inf, Inf, shelf_center_max(2), Inf];
shelf_center = shapeRectangleByCorners(grid, min_center, max_center);
min_right = [shelf_right_min(1), -Inf, -Inf, -Inf];
max_right = [shelf_right_max(1), Inf, shelf_right_max(2), Inf];
shelf_right = shapeRectangleByCorners(grid, min_right, max_right);
min_left = [shelf_left_min(1), -Inf, shelf_left_min(2), -Inf];
max_left = [shelf_left_max(1), Inf, Inf, Inf];
shelf_left = shapeRectangleByCorners(grid, min_left, max_left);
shelves_global = min(min(shelf_center, shelf_right), shelf_left);

params = default_params;
params.label = 'FRS';
params.g = grid;
params.isBackwards = false;
params.figNum = 1;
params.T = 7.0;  % seconds
params.target = shapeCylinder(params.g, [2, 4], [0; 0; 0; 0], 0.1);
params.is_reach_colors = true;
params.isTube = true;
params.videoFilename = [save_path 'reach_BRS'];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);

%%
% Compute avoid shelf in global grid
params = default_params;
params.label = 'grid_global_avoid_shelf';
params.g = grid;
% assume almost worst case
params.dMax = [0.0, dWorstCase, 0.0, dWorstCase]; 
params.figNum = 6;
params.isBackwards = true; % BRS
params.is_avoid = true;
params.T = 2;
params.target = shelves_global;
params.is_avoid_colors = true;
params.isTube = true;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);
grid_global_avoid_shelf = data.value_function(:, :, :, :, end);


%% Compute reach RCIS of inspection zone
params = default_params;
params.label = 'grid_global_reach_avoid_shelf';
params.g = grid;
params.figNum = 2;
params.isBackwards = true;  % BRS
params.T = 3;
% Using directly avoid from same grid
% global_grid_avoid = migrateGrid(grid_zone_a, grid_global_avoid_shelf, grid');
params.target = grid_global_avoid_shelf;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);
%%

% Compute reach RCIS of inspection zone
params = default_params;
params.label = 'global_grid_reach_inspect_zone_a_rcis';
params.g = grid;
params.figNum = 2;
params.isBackwards = true; % BRS
params.T = 12;
rcis_inspect_zone_a_global = migrateGrid(grid_zone_a, rcis_inspect_zone_a, grid');
params.target = rcis_inspect_zone_a_global;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);

%%
% Compute reach RCIS of inspection zone
params = default_params;
params.label = 'grid_global_reach_inspect_zone_b_rcis';
params.g = grid;
params.figNum = 3;
params.isBackwards = true; % BRS
params.T = 12;
rcis_inspect_zone_b_global = migrateGrid(grid_zone_b, rcis_inspect_zone_b, grid');
params.target = rcis_inspect_zone_b_global;
params.obstacle = shelves_global;
params.is_reach_colors = true;
params.isTube = false;
params.videoFilename = [save_path params.label];
data = quad_RS(params);
export_to_mat(save_path, params.label,  data);