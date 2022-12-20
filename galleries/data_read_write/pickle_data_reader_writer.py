import os
import pickle
from typing import Generator

from galleries import files_utils
from galleries.collections.stream_dictionary import StreamDictionary
from galleries.data_read_write.idata_reader_writer import IDataReaderWriter
from galleries.data_read_write.utils_file_data_readers_writers import *


class PickleDataReaderWriter(IDataReaderWriter):

    def __init__(self, data_identifier, root_folder: str, file_path: str = None, batch_size=100000):
        super().__init__(data_identifier)
        self._root_folder = root_folder
        if file_path is None:
            self.set_data_identifier(data_identifier)
        else:
            self._file_path = file_path

        self._batch_size = batch_size
        self._file = None

    def set_data_identifier(self, data_identifier: DataIdentifier):
        indices = read_index_list(self._root_folder, self._data_identifier)
        add_generator_to_indices_if_not_exists(self._data_identifier, indices)
        write_indices(self._root_folder, self._data_identifier, indices)
        file_path = get_data_path(self._root_folder, self._data_identifier, indices)
        files_utils.create_file_if_doesnt_exist(file_path)
        self._file_path = file_path

    def read_all_data(self) -> Generator:
        if os.path.exists(self._file_path):
            self.release()
            self._file = open(self._file_path, "rb")
            end_reached = False
            try:
                while not end_reached:
                    try:
                        row_data = pickle.load(self._file)
                        yield row_data
                    except EOFError:
                        end_reached = True
            finally:
                self.release()

    def read_data(self, indices) -> Generator:
        sd = StreamDictionary(self.read_all_data, self._batch_size)
        for index in indices:
            data, success = sd.try_get_item(index)
            yield index, data

    def write_data(self, data: Generator, notify_function=None, notify_rate=100):
        if not os.path.exists(self._file_path):
            files_utils.create_dir_of_file(self._file_path)
        file = open(self._file_path, "ab")
        try:
            def write(d):
                pickle.dump(d, file)

            IDataReaderWriter.write_data_with_notifications(data, write, notify_function, notify_rate)
        finally:
            file.close()

    def clear_data(self):
        file = open(self._file_path, "wb")
        file.close()

    def release(self):
        if self._file is not None:
            self._file.close()
            self._file = None
