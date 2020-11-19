function N = N_from_resolution(grid_min, grid_max, resolution)
    N = round((grid_max-grid_min) ./ resolution);
end

