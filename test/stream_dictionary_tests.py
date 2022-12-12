import os
import unittest

from galleries.collections.stream_dictionary import StreamDictionary
from galleries.data_read_write import default_reader_writer


class StreamDictionaryTests(unittest.TestCase):

    def setUp(self) -> None:
        self.file_path = "file.pkl"
        self.batch_size = 5
        self.test_data_size = 100
        self.test_data = {k: str(k) for k in range(self.test_data_size)}
        self._write_test_data()
        self.fsd = StreamDictionary(self._generator_provider, self.batch_size)

    def tearDown(self) -> None:
        self.default_rw.release()
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def _generator_provider(self):
        return self.default_rw.read_data(self.file_path)

    def _write_test_data(self):
        self.default_rw = default_reader_writer()
        data = self.test_data.items()
        self.default_rw.write_data(data, self.file_path)
        self.default_rw.release()
        self.default_rw = default_reader_writer()

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


if __name__ == '__main__':
    unittest.main()
