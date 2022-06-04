function uOpt = optCtrl(obj, ~, x, deriv, uMode)
% uOpt = optCtrl(obj, t, y, deriv, uMode)

%% Input processing
if nargin < 5
  uMode = 'min';
end

if ~iscell(deriv)
  deriv = num2cell(deriv);
end

%% Optimal control
if strcmp(uMode, 'max')

  if any(obj.dims == 3) % heading
    uOpt{1} = ...
      (x{obj.dims==4}>=0).*(deriv{obj.dims==3}>=0)*obj.sMax + ...
      (x{obj.dims==4}>=0).*(deriv{obj.dims==3}<0)*(-obj.sMax) + ...
      (x{obj.dims==4}<0).*(deriv{obj.dims==3}>=0)*(-obj.sMax) + ...
      (x{obj.dims==4}<0).*(deriv{obj.dims==3}<0)*obj.sMax;
  end

  if any(obj.dims == 4) % velocity
    uOpt{2} = (deriv{obj.dims==4}>=0)*obj.aMax + ...
      (deriv{obj.dims==4}<0)*(obj.aMin);
  end

elseif strcmp(uMode, 'min')

  if any(obj.dims == 3) % heading
    uOpt{1} = ...
      (x{obj.dims==4}>=0).*(deriv{obj.dims==3}>=0)*(-obj.sMax) + ...
      (x{obj.dims==4}>=0).*(deriv{obj.dims==3}<0)*obj.sMax + ...
      (x{obj.dims==4}<0).*(deriv{obj.dims==3}>=0)*obj.sMax + ...
      (x{obj.dims==4}<0).*(deriv{obj.dims==3}<0)*(-obj.sMax);
  end

  if any(obj.dims == 4) % velocity
    uOpt{2} = (deriv{obj.dims==4}>=0)*(obj.aMin) + ...
      (deriv{obj.dims==4}<0)*obj.aMax;
  end

else
  error('Unknown uMode!')
end

end