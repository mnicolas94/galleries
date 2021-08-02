import abc
import numpy as np
import pickle
from typing import Any

from galleries import files_utils


class IGallery(abc.ABC):
	"""
	Interfaz para implementar el acceso a una galería de imágenes y sus anotaciones
	"""

	@abc.abstractmethod
	def get_paths(self):
		"""
		Obtener las direcciónes de las imágenes.
		:return:
		"""
		pass

	@abc.abstractmethod
	def get_annotations_by_path(self, img_path):
		"""
		Obtener las anotaciones de una imagen dada su dirección.
		:param img_path:
		:return:
		"""
		pass

	@abc.abstractmethod
	def get_image_by_index(self, index: Any) -> np.ndarray:
		pass

	@staticmethod
	def write_gallery(gallery: 'IGallery', file_path: str):
		files_utils.create_dir_of_file(file_path)
		file = open(file_path, 'wb')
		pickle.dump(gallery, file)
		file.close()

	@staticmethod
	def read_gallery(file_path: str) -> 'IGallery':
		file = open(file_path, 'rb')
		gallery = pickle.load(file)
		file.close()
		return gallery
