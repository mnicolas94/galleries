import abc
from typing import Dict, Optional


class GalleryAnnotationsParser(abc.ABC):

	@abc.abstractmethod
	def get_annotations_by_image_index(self, img_index: str) -> dict:
		"""
		Returns a dictionary of an image annotations
		:param img_index:
		:return:
		"""
		pass

	@abc.abstractmethod
	def get_annotations_types(self) -> Optional[Dict[str, type]]:
		"""
		Returns a dictionary of each annotation's type. Also, you can get all annotations names from the
		dictionary's keys. Returns None if annotations names and types are unknown.
		:return:
		"""
		pass
