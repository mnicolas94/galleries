import abc
from typing import Generator, Callable


class IFileDataReaderWriter:

    @abc.abstractmethod
    def read_data(self, file_path: str) -> Generator:
        pass

    @abc.abstractmethod
    def write_data(
            self,
            data: Generator,
            file_path: str,
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

            notify_function = notify_function or IFileDataReaderWriter._default_notify_function
            count = i + 1
            if count % notify_rate == 0:
                notify_function(count)

    @staticmethod
    def _default_notify_function(count):
        print(f"Data written: {count}")
