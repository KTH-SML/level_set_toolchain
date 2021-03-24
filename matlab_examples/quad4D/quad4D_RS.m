function [g, data, tau2] = quad4D_RS(params)

% TODO: clean up this list
% Current possible params:
% T, isBackwards, g, is_avoid, is_boundary_avoid, target, should_cover,
% should_intersect, stop_converge, obstacle, uMin, uMax, xinit,
% figNum, is_reach_colors, is_avoid_colors, makeVideo, videoFilename,
% isTube

% Time vector
t0 = 0;
tMax = params.T;
dt = 0.05;
tau = t0:dt:tMax;

% Grid
g = params.g;
grid_min = g.min;
grid_max = g.max;

% Target set
R = 0.1;
if isfield(params, 'isBackwards') && params.isBackwards % BRS
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
        data0 = shapeCylinder(g, [], [0; 0; 0; 0], R); % creates sphere
    end
    
    if isfield(params, 'is_boundary_avoid') && params.is_boundary_avoid
        % TODO: clean this up
        boundary0 = shapeRectangleByCorners(g, ...
                [-Inf, -Inf,-Inf, -Inf], [grid_min(1)+0.1, Inf, Inf, Inf]);
        boundary1 = shapeRectangleByCorners(g, ...
            [grid_max(1)-0.1, -Inf, -Inf, -Inf], [Inf, Inf, Inf, Inf]);
        boundary2 = shapeRectangleByCorners(g, ...
            [-Inf, -Inf, -Inf, -Inf], [Inf, Inf, grid_min(3)+0.1, Inf]);
        boundary3 = shapeRectangleByCorners(g, ...
            [-Inf, -Inf, grid_max(3)-0.1, -Inf], [Inf, Inf, Inf, Inf]);
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
else % FRS
    if isfield(params, 'g')
        g = params.g;
        grid_min = g.min;
        grid_max = g.max;
        N = g.N;
    end
    
    uMode = 'max';
    dMode = 'min';
    schemeData.tMode = 'forward'; %for FRS
    
    if isfield(params, 'target')
        data0 = params.target;
    else
        data0 = shapeCylinder(g, [], [0; 0; 0; 0], R); % creates sphere
    end
end

HJIextraArgs.targetFunction = data0;

if isfield(params, 'obstacle')
    HJIextraArgs.obstacleFunction = params.obstacle;
end

% Define dynamic system
uMin = params.uMin; % TODO: make these optional
uMax = params.uMax;
if isfield(params, 'xinit')
    quad = Quad4D(params.xinit, uMin, uMax);
else
    quad = Quad4D([0, 0, 0, 0], uMin, uMax);
end

% Put grid and dynamic systems into schemeData
schemeData.grid = g;
schemeData.dynSys = quad;
schemeData.accuracy = 'low'; %set accuracy
schemeData.uMode = uMode;
schemeData.dMode = dMode;

% Compute value function
% TODO: fix plotting to be 2D
if isfield(params, 'figNum')
    HJIextraArgs.visualize.initialValueSet = true;
    HJIextraArgs.visualize.valueSet = true;
    HJIextraArgs.visualize.figNum = params.figNum; %set figure number
    HJIextraArgs.visualize.deleteLastPlot = true; %delete previous plot as you update
    
    HJIextraArgs.visualize.xTitle = "x";
    HJIextraArgs.visualize.yTitle = "vx";
    HJIextraArgs.visualize.zTitle = "y";

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

[data, tau2, ~] = ...
  HJIPDE_solve(data0, tau, schemeData, mode, HJIextraArgs);
end

