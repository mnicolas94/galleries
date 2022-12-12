import abc
from typing import Generator, Callable


class IDataReaderWriter:

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
            append: bool = False,
            notify_function: Callable = None,
            notify_rate=100):
        pass

    @abc.abstractmethod
    def release(self):
        pass

    @staticmethod
    def _write_data_with_notifications(data, data_writer_function, notify_function, notify_rate):
        for i, d in enumerate(data):
            data_writer_function(d)

            notify_function = notify_function or IDataReaderWriter._default_notify_function
            count = i + 1
            if count % notify_rate == 0:
                notify_function(count)

    @staticmethod
    def _default_notify_function(count):
        print(f"Data written: {count}")