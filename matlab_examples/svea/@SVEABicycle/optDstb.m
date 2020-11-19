function dOpt = optDstb(obj, ~, ~, deriv, dMode)
% Dynamics of Simple Car:
%    \dot{x}_1 = x_4 * cos(x_3)       + d1
%    \dot{x}_2 = x_4 * sin(x_3)       + d2
%    \dot{x}_3 = (x_4 * tan(u1))/L    + d3
%    \dot{x}_4 = u2                   + d4

%% Input processing
if nargin < 5
  dMode = 'max';
end

if ~iscell(deriv)
  deriv = num2cell(deriv);
end

dOpt = cell(obj.nd, 1);

%% Optimal control
if strcmp(dMode, 'max')
  for i = 1:4
    if any(obj.dims == i)
      dOpt{i} = (deriv{obj.dims==i}>=0)*obj.dMax(i) + ...
        (deriv{obj.dims==i}<0)*(-obj.dMax(i));
    end
  end

elseif strcmp(dMode, 'min')
  for i = 1:4
    if any(obj.dims == i)
      dOpt{i} = (deriv{obj.dims==i}>=0)*(-obj.dMax(i)) + ...
        (deriv{obj.dims==i}<0)*obj.dMax(i);
    end
  end
else
  error('Unknown dMode!')
end

end