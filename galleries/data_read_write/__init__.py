from galleries.data_read_write.pickle_data_reader_writer import PickleDataReaderWriter
from galleries.data_read_write.sqlite_data_reader_writer import SqliteDataReaderWriter


def default_reader_writer():
    """
    Deprecated.
    :return:
    """
    return PickleDataReaderWriter()
    # return SqliteDataReaderWriter()


def get_pickle_data_reader_writer(gallery_name: str, data_type: str, algorithm_id: str):
    pass