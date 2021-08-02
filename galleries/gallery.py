import cv2 as cv
from typing import Any

import numpy as np

from galleries.abstract_gallery import AbstractGallery
from galleries import files_utils


class Gallery(AbstractGallery):


	def __init__(self, directory, annots_parser, recursive=False):
		"""
		:param directory: directorio de la galería.
		:param annots_parser: parser para obtener las anotaciones de una imagen.
		:param recursive:
		"""
		self._directory = directory
		self._recursive = recursive
		self._annots_parser = annots_parser

	@property
	def directory(self):
		return self._directory

	@directory.setter
	def directory(self, value):
		self._directory = value

	@property
	def recursive(self):
		return self._recursive

	@recursive.setter
	def recursive(self, value):
		self._recursive = value

	@property
	def annotations_parser(self):
		return self._annots_parser

	@annotations_parser.setter
	def annotations_parser(self, value):
		self._annots_parser = value

	def get_paths(self):
		return files_utils.list_images(self._directory, recursive=self._recursive)

	def get_annotations_by_path(self, img_path):
		return self._annots_parser(img_path)

	def get_image_by_index(self, index: Any) -> np.ndarray:
		img_path: str = index
		return cv.imread(img_path)
