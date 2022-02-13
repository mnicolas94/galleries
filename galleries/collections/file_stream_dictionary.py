import pickle
from typing import Any

from mnd_utils.datastructures.circular_generator import CircularGenerator


class FileStreamDictionary:

    def __init__(self, file_path, batch_size):
        self._file_path = file_path
        self._batch_size = batch_size
        self._circular_generator = CircularGenerator(self._get_generator)

        self._all_loaded = False
        self._current_batch: dict = None

    def _get_generator(self):
        file = open(self._file_path, "rb")
        end_reached = False
        while not end_reached:
            try:
                row_data = pickle.load(file)
                yield row_data
            except EOFError:
                end_reached = True
        file.close()

    def _get_current_batch_dict(self):
        if self._current_batch is None:
            # initialize batch
            self._load_next_batch()
            if len(self._current_batch) < self._batch_size:
                self._all_loaded = True
        return self._current_batch

    def _load_next_batch(self):
        print("*** loading batch...")
        size = self._batch_size
        gen = self._circular_generator[:size]
        self._current_batch = {index: value for index, value in gen}

    def try_get_item(self, key) -> (Any, bool):
        try:
            value = self[key]
            return value, True
        except KeyError:
            return None, False

    def __getitem__(self, key):
        batch = self._get_current_batch_dict()
        if key in batch:
            return batch[key]
        # else
        if self._all_loaded:
            raise KeyError(key)
        first_key = next(iter(batch.keys()))
        while True:
            self._load_next_batch()
            found = key in self._current_batch
            if found:
                return self._current_batch[key]

            first_key_again = first_key in self._current_batch
            if first_key_again:
                raise KeyError(key)

    def __iter__(self):
        return self._get_generator()
