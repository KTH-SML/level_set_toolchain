function save_path = export_to_mat(save_path, label, data)
    save([save_path label], 'data', '-v7.3');
end