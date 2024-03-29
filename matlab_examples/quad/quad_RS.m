function data = quad_RS(params)

% TODO: clean up this list
% Current possible params:
% T, isBackwards, g, is_avoid, is_boundary_avoid, target, should_cover,
% should_intersect, stop_converge, obstacle, uMin, uMax, xinit,
% figNum, is_reach_colors, is_avoid_colors, makeVideo, videoFilename,
% isTube

% Time vector
t0 = 0;
tMax = params.T;
dt = params.dt;
tau = t0:dt:tMax;

% Grid
grid = params.g;
grid_min = grid.min;
grid_max = grid.max;

% Target set
R = 0.1;
if isfield(params, 'isBackwards') && params.isBackwards
    % BRS
    if (isfield(params, 'is_avoid') && params.is_avoid) || ...
       (isfield(params, 'is_boundary_avoid') && params.is_boundary_avoid)
        uMode = 'max';
        dMode = 'min';
    else
        uMode = 'min';
        dMode = 'max';
    end
    
    if isfield(params, 'target')
        data0 = params.target;
    else
        data0 = shapeCylinder(grid, [], [0; 0; 0; 0], R); % creates sphere
    end
    
    if isfield(params, 'is_boundary_avoid') && params.is_boundary_avoid
        % TODO: clean this up
        boundary0 = shapeRectangleByCorners(grid, ...
                [-Inf, -Inf,-Inf, -Inf], [grid_min(1)+0.15, Inf, Inf, Inf]);
        boundary1 = shapeRectangleByCorners(grid, ...
            [grid_max(1)-0.15, -Inf, -Inf, -Inf], [Inf, Inf, Inf, Inf]);
        boundary2 = shapeRectangleByCorners(grid, ...
            [-Inf, -Inf, -Inf, -Inf], [Inf, Inf, grid_min(3)+0.15, Inf]);
        boundary3 = shapeRectangleByCorners(grid, ...
            [-Inf, -Inf, grid_max(3)-0.15, -Inf], [Inf, Inf, Inf, Inf]);
        data0 = min(min(min(boundary0, boundary1), boundary2), boundary3);
        
        if isfield(params, 'target')
            data0 = min(data0, params.target);
        end
    end
    
    if isfield(params, 'should_cover')
        HJIextraArgs.stopSetInclude = params.should_cover;
    elseif isfield(params, 'should_intersect')
        HJIextraArgs.stopSetIntersect = params.should_intersect;
    elseif isfield(params, 'stop_converge')
        HJIextraArgs.stopConverge = params.stop_converge;
    end
else
    % FRS
    if isfield(params, 'g')
        grid = params.g;
        grid_min = grid.min;
        grid_max = grid.max;
        N = grid.N;
    end
    
    uMode = 'max';
    dMode = 'min';
    schemeData.tMode = 'forward';
    
    if isfield(params, 'target')
        data0 = params.target;
    else
        data0 = shapeCylinder(grid, [], [0; 0; 0; 0], R); % creates sphere
    end
end

HJIextraArgs.targetFunction = data0;

if isfield(params, 'obstacle')
    HJIextraArgs.obstacleFunction = params.obstacle;
end

% Define dynamic system
uMin = params.uMin; % TODO: make these optional
uMax = params.uMax;
dMax = params.dMax;
if isfield(params, 'xinit')
    quad = QuadDisturb(params.xinit, uMin, uMax, dMax);
else
    quad = QuadDisturb([0, 0, 0, 0], uMin, uMax, dMax);
end

% Put grid and dynamic systems into schemeData
schemeData.grid = grid;
schemeData.dynSys = quad;
schemeData.accuracy = params.accuracy; %set accuracy
schemeData.uMode = uMode;
schemeData.dMode = dMode;

% Compute value function
if isfield(params, 'figNum')
    HJIextraArgs.visualize.initialValueSet = true;
    HJIextraArgs.visualize.valueSet = true;
    HJIextraArgs.visualize.figNum = params.figNum;
    HJIextraArgs.visualize.deleteLastPlot = true;
    
    HJIextraArgs.visualize.plotData.plotDims = [1; 0; 1; 0];
    HJIextraArgs.visualize.plotData.projpt = [0.0; 0.0];

    HJIextraArgs.visualize.xTitle = "x (m)";
    HJIextraArgs.visualize.yTitle = "y (m)";

    if isfield(params, 'is_reach_colors')
        HJIextraArgs.visualize.plotColorVS0 = 'g';
        HJIextraArgs.visualize.plotColorVS = 'b';
    elseif isfield(params, 'is_avoid_colors')
        HJIextraArgs.visualize.plotColorVS0 = 'k';
        HJIextraArgs.visualize.plotColorVS = 'r';
    end
    
    if isfield(params, 'makeVideo') && params.makeVideo
        HJIextraArgs.makeVideo = true;
        if isfield(params, 'videoFilename')
            HJIextraArgs.videoFilename = params.videoFilename;
        end
    end
end

if isfield(params, 'isTube') && params.isTube
    mode = 'minVOverTime';
else
    mode = 'none';
end

HJIextraArgs.quiet = true;

if isfield(params, 'label')
    fprintf('Generate reachable data for %s: \n', params.label);
end

[value_function, time, ~] = ...
  HJIPDE_solve(data0, tau, schemeData, mode, HJIextraArgs);

%% Parse output data
data.grid = grid;
data.value_function = value_function;
data.time = time;

if isfield(params, 'label')
    set_figure_title(params.label);
end

end

