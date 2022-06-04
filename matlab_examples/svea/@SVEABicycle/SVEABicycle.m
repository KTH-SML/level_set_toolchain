classdef SVEABicycle < DynSys
  properties
    sMax    % Steering bound (assumed symmetric)
    aMax    % Acceleration upper-bound (throttle)
    aMin    % Acceleration lower-bound (brake)    
    dMax    % Additive disturbance bounds
    L       % Vehicle wheel base length
    dims    % Dimensions that are active
  end
  
  methods
    function obj = SVEABicycle(x, sMax, aMax, aMin, dMax, L, dims)
      % obj = SVEABicycle(x, sMax, aMax, dMax, dims)
      %     Bicycle Model Car class tailored for SVEA
      %
      % Dynamics:
      %    \dot{x}_1 = x_4 * cos(x_3)       + d1
      %    \dot{x}_2 = x_4 * sin(x_3)       + d2
      %    \dot{x}_3 = (x_4 * tan(u1))/L    + d3
      %    \dot{x}_4 = u2                   + d4
      %         u1 \in [-sMax, sMax]
      %         u2 \in [aMin, aMax]
      %         d \in [-dMax, dMax]
      %
      % Inputs:
      %   x      - state: [xpos; ypos; theta; v]
      %   sMax   - maximum steering
      %   aMax   - maximum acceleration
      %   dMax   - disturbance bounds
      %   L      - length of vehicle
      %
      % Output:
      %   obj       - a SVEABicycle object
      
      if numel(x) ~= obj.nx
        error('Initial state does not have right dimension!');
      end
      
      if ~iscolumn(x)
        x = x';
      end
      
      if nargin < 2
        sMax = pi/4;
      end
      
      if nargin < 3
        aMax = 1.5;
      end
      
      if nargin < 4
        aMin = -1.0; % Trying to be conservative (brake early)
      end
      
      if nargin < 5
        dMax = [0; 0; 0; 0.0]; %
      end
            
      if nargin < 6
          L = 0.32;
      end
      
      if nargin < 7
        dims = 1:4;
      end
      
      % Basic vehicle properties
      obj.pdim = [find(dims == 1) find(dims == 2)]; % Position dimensions
      obj.hdim = find(dims == 3);   % Heading dimension
      obj.vdim = find(dims == 4);   % Velocity dimension
      obj.nx = length(dims);
      obj.nu = 2;
      obj.nd = 4;
      
      obj.x = x;
      obj.xhist = obj.x;
      
      obj.L = L; % wheel base of vehicle
      
      obj.sMax = sMax;
      obj.aMax = aMax;
      obj.aMin = aMin;
      obj.dMax = dMax;
      obj.dims = dims;
    end
    
  end
end
