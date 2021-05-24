function grid = create_grid_from_resolution(grid_min, grid_max, resolution)
    N = round((grid_max - grid_min) ./ resolution);
    grid = createGrid(grid_min, grid_max, N);   
end

