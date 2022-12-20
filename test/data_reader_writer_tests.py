import abc
import os
import unittest

from galleries.data_read_write import PickleDataReaderWriter, SqliteDataReaderWriter
from galleries.data_read_write.idata_reader_writer import IDataReaderWriter
from test.test_utils import TestGallery

from test.test_utils_data_reading_writing import write_data


class DataReaderWriterTests(unittest.TestCase):

    def setUp(self) -> None:
        self.file_path = "file.pkl"
        self.rw: IDataReaderWriter = self._get_reader_writer(self.file_path)
        self.gallery = TestGallery("Test", 100)

    def tearDown(self) -> None:
        self.rw.release()
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    @abc.abstractmethod
    def _get_reader_writer(self, file_path):
        pass

    def _get_data(self, img):
        return img.sum()

    def test_when_write_data__read_the_same(self):
        # arrange
        write_data(self.gallery, self._get_data, self.rw)

        # act
        data = self.rw.read_all_data()

        # assert
        for i, d in data:
            img = self.gallery.get_image_by_index(i)
            expected = self._get_data(img)
            self.assertEqual(expected, d)

    def test_when_read_without_writing__read_data_returns_empty_generator(self):
        # act
        data = self.rw.read_all_data()
        data_list = list(data)

        # assert
        self.assertEqual(0, len(data_list))

    def test_when_read_indices__data_is_correct(self):
        # arrange
        write_data(self.gallery, self._get_data, self.rw)
        indices = (i for i in range(45, 65))  # arbitrary range

        # act
        data = self.rw.read_data(indices)

        # assert
        for i, d in data:
            img = self.gallery.get_image_by_index(i)
            expected = self._get_data(img)
            self.assertEqual(expected, d)


class PickleDataReaderWriterTests(DataReaderWriterTests):

    def _get_reader_writer(self, file_path):
        return PickleDataReaderWriter(None, "", file_path, 100)


class SqliteDataReaderWriterTests(DataReaderWriterTests):

    def _get_reader_writer(self, file_path):
        return SqliteDataReaderWriter(None, "", file_path, 100)


if __name__ == '__main__':
    unittest.main()
