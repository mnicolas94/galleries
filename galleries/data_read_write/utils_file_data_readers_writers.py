import os
from pathlib import Path

from galleries.data_read_write.idata_reader_writer import DataIdentifier


SEP = ' '
EXT = 'gdat'


def _get_folder_dir(root_folder: str, data_identifier: DataIdentifier):
    gallery_name = data_identifier.gallery_name
    data_type = data_identifier.data_type_id
    folder_dir = os.path.join(root_folder, gallery_name, data_type)
    return folder_dir


def get_data_path(root_folder: str, data_identifier: DataIdentifier, indices):
    data_file = None
    if len(indices) > 0:
        unique_id = data_identifier.algorithm_id
        for index, uid in indices:
            if uid == unique_id:
                data_generator_folder = _get_folder_dir(root_folder, data_identifier)
                data_file = os.path.join(data_generator_folder, f'{index}.{EXT}')
                break
    return data_file


def get_index_path(root_folder: str, data_identifier: DataIdentifier):
    folder = _get_folder_dir(root_folder, data_identifier)
    file_path = os.path.join(folder, 'index.txt')
    return file_path


def read_index_list(root_folder: str, data_identifier: DataIdentifier):
    indices = []
    index_file = get_index_path(root_folder, data_identifier)
    if os.path.exists(index_file):
        with open(index_file) as file:
            for line in file:
                line = line.strip()
                index, unique_id = line.split(sep=SEP, maxsplit=1)
                index = int(index)
                indices.append((index, unique_id))
    return indices


def write_indices(root_folder: str, data_identifier: DataIdentifier, indices):
    index_file = get_index_path(root_folder, data_identifier)
    directory = Path(index_file).parent
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(index_file, 'w') as file:
        for index, conf in indices:
            file.write(f'{index}{SEP}{conf}\n')


def add_generator_to_indices_if_not_exists(data_identifier: DataIdentifier, indices: list) -> bool:
    unique_id = data_identifier.algorithm_id
    exists = False
    max_index = -1
    for index, configuration in indices:
        if index > max_index:
            max_index = index
        if configuration == unique_id:
            exists = True
            break
    if not exists:
        indices.append((max_index + 1, unique_id))
    return not exists
