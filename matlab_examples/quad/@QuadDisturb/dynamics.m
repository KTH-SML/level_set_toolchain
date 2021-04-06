function dx = dynamics(obj, ~, x, u, d)
% dx = dynamics(obj, t, x, u, d)
%     Dynamics of the quadrotor

if nargin < 5
  d = [0; 0; 0; 0];
end

dx = cell(obj.nx,1);
dims = obj.dims;

returnVector = false;
if ~iscell(x)
  returnVector = true;
  x = num2cell(x);
  u = num2cell(u);
  d = num2cell(d);
end

for i = 1:length(dims)
  dx{i} = dynamics_cell_helper(x, u, d, dims, dims(i));
end

if returnVector
  dx = cell2mat(dx);
end
end

function dx = dynamics_cell_helper(x, u, d, dims, dim)

switch dim
  case 1
    dx = x{dims==2} + d{1};
  case 2
    dx = u{1} + d{2};
  case 3
    dx = x{dims==4} + d{3};
  case 4
    dx = u{2} + d{4};
  otherwise
    error('Only dimensions 1-4 are defined for dynamics of Quad4DC!')
end
end