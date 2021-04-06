classdef QuadDisturb < DynSys
  properties
    dims    % Active dimensions
    uMin    % Control bounds
    uMax
    dMax    % Additive disturbance bounds
  end % end properties
  
  methods
    function obj = QuadDisturb(x, uMin, uMax, dMax, dims)
      % obj = QuadDisturb(x, uMin, uMax, dMax)
      %
      % Constructor. Creates a quadrotor object with a unique ID,
      % state x, and reachable set information reachInfo
      %
      % Dynamics:
      %    \dot{p}_x = v_x + d1
      %    \dot{v}_x = u_x + d2
      %    \dot{p}_y = v_y + d3
      %    \dot{v}_y = u_y + d4
      %       uMin <= u_x <= uMax
      %       d \in [-dMax, dMax]
      %
      % Inputs:   x   - state: [xpos; xvel; ypos; yvel]
      % Output:   obj - a quadrotor object
      
      % Make sure initial state is a column vector
      if ~iscolumn(x)
        x = x';
      end
      
      if nargin < 2
        uMax = 3;
        uMin = -3;
      end
      
      if nargin < 4
        dMax = [0.0, 0.0, 0.0, 0.0];
      end
      
      if nargin < 5
        dims = 1:4;
      end
      
      obj.x = x;
      obj.xhist = x;
      
      obj.uMax = uMax;
      obj.uMin = uMin;
      obj.dMax = dMax;
      
      obj.pdim = [find(dims == 1) find(dims == 3)]; % Position dimensions
      obj.vdim = [find(dims == 2) find(dims == 4)]; % Velocity dimensions
      
      obj.nu = 2;
      obj.dims = dims;
      obj.nx = length(dims);
      obj.nd = 4;
      
      if numel(x) ~= obj.nx
        error('Initial state does not have right dimension!');
      end
      
    end % end constructor
  end % end methods
end % end class