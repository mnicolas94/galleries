import os
import unittest

from galleries.collections.file_stream_dictionary import FileStreamDictionary
from galleries.data_read_write import PickleDataReaderWriter


class FileStreamDictionaryTests(unittest.TestCase):

    def setUp(self) -> None:
        self.file_path = "file.pkl"
        self.batch_size = 5
        self.test_data_size = 100
        self.test_data = {k: str(k) for k in range(self.test_data_size)}
        self.default_rw = PickleDataReaderWriter(None, "", self.file_path)
        self.fsd = FileStreamDictionary(self.file_path, self.batch_size, data_reader_writer=self.default_rw)
        self._write_test_data()

    def tearDown(self) -> None:
        self.fsd.close()
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def _write_test_data(self):
        data = self.test_data.items()
        self.default_rw.write_data(data)
        self.default_rw.release()

    def test_read_all_data(self):
        # arrange
        indices = range(self.test_data_size)

        # act and assert
        for i in indices:
            v = self.fsd[i]
            self.assertTrue(str(i) == v)

    def test_read_all_data_with_try_get_item(self):
        # arrange
        indices = range(self.test_data_size)

        # act and assert
        for i in indices:
            v, success = self.fsd.try_get_item(i)
            self.assertTrue(success)
            self.assertTrue(str(i) == v)

    def test_read_all_data_as_iterator(self):
        # arrange

        # act and assert
        for i, data in self.fsd:
            expected = self.test_data[i]
            self.assertEqual(expected, data)

    def test_read_data_raises_exception_after_closing(self):
        # arrange

        # act
        self.fsd.close()
        # assert
        self.assertRaises(IOError, self.fsd.__getitem__, 0)

    def test_try_get_item_doesnt_exists_returns_not_success(self):
        # arrange
        s = self.test_data_size
        not_existent_indices = [-1, s, s + 1, s * 2]

        # act and assert
        for i in not_existent_indices:
            v, success = self.fsd.try_get_item(i)
            self.assertFalse(success)

    def test_get_item_doesnt_exists_raises_exception(self):
        # arrange
        s = self.test_data_size
        not_existent_indices = [-1, s, s + 1, s * 2]

        # act and assert
        for i in not_existent_indices:
            self.assertRaises(KeyError, self.fsd.__getitem__, i)

    def test_push_new_data(self):
        # arrange
        new_index = self.test_data_size
        new_value = str(new_index)

        # false positive assert
        _, success = self.fsd.try_get_item(new_index)
        self.assertFalse(success)

        # act
        self.fsd.push_data(new_index, new_value)

        # assert
        v = self.fsd[new_index]
        self.assertTrue(v == new_value)

    def test_push_new_data_maintains_old_data(self):
        # arrange
        old_index = 0
        new_index = self.test_data_size
        new_value = str(new_index)

        # false positive assert
        _, success_new = self.fsd.try_get_item(new_index)
        old_value, success_old = self.fsd.try_get_item(old_index)
        self.assertFalse(success_new)
        self.assertTrue(success_old)

        # act
        self.fsd.push_data(new_index, new_value)

        # assert
        v = self.fsd[old_index]
        self.assertTrue(v == old_value)

    def test_pushed_data_persists_after_closing(self):
        # arrange
        new_index = self.test_data_size
        new_value = str(new_index)

        # false positive assert
        _, success_new = self.fsd.try_get_item(new_index)
        self.assertFalse(success_new)

        # act
        self.fsd.push_data(new_index, new_value)
        self.fsd.close()
        self.fsd = FileStreamDictionary(self.file_path, self.batch_size)

        # assert
        v = self.fsd[new_index]
        self.assertTrue(v == new_value)


if __name__ == '__main__':
    unittest.main()
