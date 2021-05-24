function save_path = store_under(directory_name)
    warning('off', 'MATLAB:MKDIR:DirectoryExists');
    path = fileparts(mfilename('fullpath'));
    save_path = [path  '/../../resources/generated/' directory_name '/'];
    mkdir(save_path);
    fprintf("Storing reachable data under %s\n", save_path);
end

