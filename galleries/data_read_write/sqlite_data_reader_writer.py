import io
import pickle

import numpy as np
import os.path
import sqlite3
from sqlite3 import Connection
from typing import Generator, Optional

from galleries import files_utils
from galleries.collections.stream_dictionary import StreamDictionary
from galleries.data_read_write.idata_reader_writer import IDataReaderWriter
from galleries.data_read_write.utils_file_data_readers_writers import *


def adapt_array(arr):
    """
    https://stackoverflow.com/a/18622264/9464297
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)


class SqliteDataReaderWriter(IDataReaderWriter):
    TABLE_NAME = "Data"

    def __init__(self, data_identifier, root_folder: str, file_path: str = None, batch_size=100000):
        super().__init__(data_identifier)
        self._root_folder = root_folder
        if file_path is None:
            self.set_data_identifier(data_identifier)
        else:
            self._file_path = file_path

        self._batch_size = batch_size
        self._connection: Optional[Connection] = None

    def set_data_identifier(self, data_identifier: DataIdentifier):
        indices = read_index_list(self._root_folder, self._data_identifier)
        add_generator_to_indices_if_not_exists(self._data_identifier, indices)
        write_indices(self._root_folder, self._data_identifier, indices)
        file_path = get_data_path(self._root_folder, self._data_identifier, indices)
        files_utils.create_file_if_doesnt_exist(file_path)
        self._file_path = file_path

    def read_all_data(self) -> Generator:
        self.release()
        self._connect(self._file_path)
        cur = self._connection.cursor()
        try:
            data = cur.execute("SELECT * FROM Data")
            for d in data:
                yield pickle.loads(d[0])
        except:
            pass
        finally:
            self.release()

    def read_data(self, indices) -> Generator:
        sd = StreamDictionary(self.read_all_data, self._batch_size)
        for index in indices:
            data, success = sd.try_get_item(index)
            yield index, data

    def write_data(self, data: Generator, notify_function=None, notify_rate=100):
        self.release()
        exists = os.path.exists(self._file_path)
        if not exists:
            files_utils.create_dir_of_file(self._file_path)

        try:
            self._connect(self._file_path)
            cur = self._connection.cursor()
            exists_table = False
            try:
                tables = cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Data'; """).fetchall()
                exists_table = tables != []
            except sqlite3.OperationalError:
                pass
            if not exists_table:
                cur.execute("CREATE TABLE Data (data BLOB)")

            def write(d):
                bd = pickle.dumps(d)
                cur.execute("INSERT INTO Data (data) VALUES(?)", [bd])
            self.write_data_with_notifications(data, write, notify_function, notify_rate)

            self._connection.commit()
        finally:
            self.release()

    def clear_data(self):
        self._connect(self._file_path)
        cur = self._connection.cursor()
        cur.execute("DELETE FROM Data")

    def release(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _connect(self, file_path):
        self.release()
        self._connection = sqlite3.connect(file_path, detect_types=sqlite3.PARSE_DECLTYPES)
