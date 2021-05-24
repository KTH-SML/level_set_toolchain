function save_path = export_to_hdf5(save_path, label, data)
    h5write([save_path label], 'label', 'data.value_function');
end