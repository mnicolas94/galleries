from typing import Callable

from galleries.data_read_write.idata_reader_writer import IDataReaderWriter
from galleries.igallery import IGallery


def get_data(gallery: IGallery, data_function: Callable):
    for img_index in gallery.get_indices():
        img = gallery.get_image_by_index(img_index)
        feats = data_function(img)
        yield img_index, feats


def write_data(gallery, data_function, data_reader_writer: IDataReaderWriter):
    data = get_data(gallery, data_function)
    data_reader_writer.write_data(data)
