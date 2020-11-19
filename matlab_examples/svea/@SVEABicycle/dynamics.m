function dx = dynamics(obj, ~, x, u, d)
% Dynamics of SVEA Bicycle:
%    \dot{x}_1 = x_4 * cos(x_3)       + d1
%    \dot{x}_2 = x_4 * sin(x_3)       + d2
%    \dot{x}_3 = (x_4 * tan(u1))/L    + d3
%    \dot{x}_4 = u2                   + d4
%         u1 \in [-sMax, sMax]
%         u2 \in [aMin, aMax]
%         d \in [-dMax, dMax]
%
%   Control: u1 = s, u2 = a;

if nargin < 5
  d = [0; 0; 0; 0];
end

if iscell(x)
  dx = cell(length(obj.dims), 1);
  
  for i = 1:length(obj.dims)
    dx{i} = dynamics_cell_helper(obj, x, u, d, obj.dims, obj.dims(i));
  end
else
  dx = zeros(obj.nx, 1);
  
  dx(1) = x(4) * cos(x(3)) + d(1);
  dx(2) = x(4) * sin(x(3)) + d(2);
  dx(3) = (x(4) * tan(u(1)))/obj.L + d(3);
  dx(4) = u(2) + d(4);
end
end

function dx = dynamics_cell_helper(obj, x, u, d, dims, dim)

switch dim
  case 1
    dx = x{dims==4} .* cos(x{dims==3}) + d{1};
  case 2
    dx = x{dims==4} .* sin(x{dims==3}) + d{2};
  case 3
    dx = (x{dims==4} .* tan(u{1})) ./obj.L + d{3};
  case 4
    dx = u{2} + d{4};
  otherwise
    error('Only dimension 1-4 are defined for dynamics of SVEA Bicycle!')
end
end