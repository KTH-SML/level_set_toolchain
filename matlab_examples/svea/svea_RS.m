function data = svea_RS(params)

% TODO: clean up this list
% Current possible params:
% T, isBackwards, g, is_avoid, is_boundary_avoid, target, should_cover,
% should_intersect, stop_converge, obstacle, sMax, aMax, aMin, xinit,
% figNum, is_reach_colors, is_avoid_colors, makeVideo, videoFilename,
% isTube

% Time vector
t0 = 0;
tMax = params.T;
dt = 0.05;
time_vector = t0:dt:tMax;

% Target set
R = 0.2;
if isfield(params, 'isBackwards') && params.isBackwards % BRS
    % Grid
    if isfield(params, 'g')
        g = params.g;
        grid_min = g.min;
        grid_max = g.max;
        N = g.N;
    end

    if (isfield(params, 'is_avoid') && params.is_avoid) || ...
       (isfield(params, 'is_boundary_avoid') && params.is_boundary_avoid)
        uMode = 'max';
        dMode = 'min';
    else
        uMode = 'min';
        dMode = 'max';
    end
    
    if isfield(params, 'target')
        initial_vf = params.target;
    else
        initial_vf = shapeCylinder(g, [], [0; 0; 0; 0], R); % creates sphere
    end
    
    if isfield(params, 'is_boundary_avoid') && params.is_boundary_avoid
        % TODO: clean this up
        boundary0 = shapeRectangleByCorners(g, ...
                [-Inf, -Inf,-Inf, -Inf], [grid_min(1)+0.32, Inf, Inf, Inf]);
        boundary1 = shapeRectangleByCorners(g, ...
            [grid_max(1)-0.32, -Inf, -Inf, -Inf], [Inf, Inf, Inf, Inf]);
        boundary2 = shapeRectangleByCorners(g, ...
            [-Inf, -Inf, -Inf, -Inf], [Inf, grid_min(2)+0.32, Inf, Inf]);
        boundary3 = shapeRectangleByCorners(g, ...
            [-Inf, grid_max(2)-0.32, -Inf, -Inf], [Inf, Inf, Inf, Inf]);
        initial_vf = min(min(min(boundary0, boundary1), boundary2), boundary3);
        
        if isfield(params, 'target')
            initial_vf = min(initial_vf, params.target);
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
    % Grid
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
        initial_vf = params.target;
    else
        initial_vf = shapeCylinder(g, [], [0; 0; 0; 0], R); % creates sphere
    end
end

HJIextraArgs.targetFunction = initial_vf;

if isfield(params, 'obstacle')
    HJIextraArgs.obstacleFunction = params.obstacle;
end

% Define dynamic system
sMax = params.sMax; % TODO: make these optional
aMax = params.aMax;
aMin = params.aMin;
if isfield(params, 'xinit')
    sCar = SVEABicycle(params.xinit, sMax, aMax, aMin);
else
    sCar = SVEABicycle([0, 0, 0, 0], sMax, aMax, aMin);
end

% Put grid and dynamic systems into schemeData
schemeData.grid = g;
schemeData.dynSys = sCar;
schemeData.accuracy = 'high'; %set accuracy
schemeData.uMode = uMode;
schemeData.dMode = dMode;

% Compute value function
if isfield(params, 'figNum')
    HJIextraArgs.visualize.initialValueSet = true;
    HJIextraArgs.visualize.valueSet = true;
    HJIextraArgs.visualize.figNum = params.figNum; %set figure number
    HJIextraArgs.visualize.deleteLastPlot = true; %delete previous plot as you update

    if isfield(params, 'is_reach_colors')
        HJIextraArgs.visualize.plotColorVS0 = 'g';
        HJIextraArgs.visualize.plotColorVS = 'b';
    elseif isfield(params, 'is_avoid_colors')
        HJIextraArgs.visualize.plotColorVS0 = 'k';
        HJIextraArgs.visualize.plotColorVS = 'r';
    end
    
    HJIextraArgs.visualize.xTitle = 'x [m]';
    HJIextraArgs.visualize.yTitle = 'y [m]';
    HJIextraArgs.visualize.zTitle = '$\theta$ [rad]';
    
    %HJIextraArgs.viewAngle = [120, 30];

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

[vf, time, ~] = ...
  HJIPDE_solve(initial_vf, time_vector, schemeData, mode, HJIextraArgs);

data.grid = g;
data.value_function = vf;
data.time = time;

end