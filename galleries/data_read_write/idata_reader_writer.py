import abc
from typing import Generator, Callable


class DataIdentifier:

    def __init__(self, gallery_name: str, data_type_id: str, algorithm_id: str):
        self._gallery_name = gallery_name
        self._data_type_id = data_type_id
        self._algorithm_id = algorithm_id

    @property
    def gallery_name(self):
        return self._gallery_name

    @property
    def data_type_id(self):
        return self._data_type_id

    @property
    def algorithm_id(self):
        return self._algorithm_id


class IDataReaderWriter:

    def __init__(self, data_identifier: DataIdentifier):
        self._data_identifier = data_identifier

    @abc.abstractmethod
    def set_data_identifier(self, data_identifier: DataIdentifier):
        pass

    @abc.abstractmethod
    def read_all_data(self) -> Generator:
        pass

    @abc.abstractmethod
    def read_data(self, indices) -> Generator:
        pass

    @abc.abstractmethod
    def write_data(
            self,
            data: Generator,
            notify_function: Callable = None,
            notify_rate=100):
        pass

    @abc.abstractmethod
    def clear_data(self):
        pass

    @abc.abstractmethod
    def release(self):
        pass

    @staticmethod
    def write_data_with_notifications(data, data_writer_function, notify_function, notify_rate):
        for i, d in enumerate(data):
            data_writer_function(d)

            notify_function = notify_function or IDataReaderWriter._default_notify_function
            count = i + 1
            if count % notify_rate == 0:
                notify_function(count)

    @staticmethod
    def _default_notify_function(count):
        print(f"Data written: {count}")
