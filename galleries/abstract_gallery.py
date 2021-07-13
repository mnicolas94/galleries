import abc
from galleries.igallery import IGallery
import cv2 as cv


class AbstractGallery(IGallery, abc.ABC):
	"""
	Especie de decorador para clases que implementen IGallery. Lo que hace es añadir métodos útiles a estas clases.
	TODO considerar implementar como decorador que añada estos métodos
	"""

	def get_paths_annots(self):
		for img_path in self.get_paths():
			yield img_path, self.get_annotations_by_path(img_path)

	def get_images(self):
		for img_path in self.get_paths():
			yield cv.imread(img_path)

	def get_images_annots(self):
		for img_path, annots in self.get_paths_annots():
			img = cv.imread(img_path)
			yield img, annots






