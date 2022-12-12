from typing import Any, Callable

from mnd_utils.datastructures.circular_generator import CircularGenerator


class StreamDictionary:

    def __init__(self, generator_provider: Callable, batch_size):
        self._generator_provider = generator_provider
        self._circular_generator = CircularGenerator(self._get_generator)
        self._closed = False
        self._all_loaded = False
        self._batch_size = batch_size
        self._current_batch: dict = None

    @property
    def closed(self):
        return self._closed

    def _get_generator(self):
        yield from self._generator_provider()

    def _get_current_batch_dict(self):
        if self._current_batch is None:
            # initialize batch
            self._load_next_batch()
            if len(self._current_batch) < self._batch_size:
                self._all_loaded = True
        return self._current_batch

    def _load_next_batch(self):
        size = self._batch_size
        gen = self._circular_generator[:size]
        self._current_batch = {}
        for index, value in gen:
            if index in self._current_batch:
                break  # turned around
            self._current_batch[index] = value

    def try_get_item(self, key) -> (Any, bool):
        try:
            value = self[key]
            return value, True
        except KeyError:
            return None, False

    def __getitem__(self, key):
        if self._closed:
            raise IOError("Error: reading closed stream")

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
        if self._closed:
            raise IOError("Error: reading closed stream")
        return self._get_generator()
