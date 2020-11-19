function [BRS_TTR, grad_theta, grad_v] = ...
    extract_useful(BRS_g, BRS_data, BRS_tau2)

BRS_TTR = TD2TTR(BRS_g, BRS_data, BRS_tau2);
grad = computeGradients(BRS_g, BRS_TTR);
grad_theta = grad{3};
grad_v = grad{4};

end

