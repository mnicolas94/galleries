import abc
import os


class GalleryAnnotationsParser(abc.ABC):

	@abc.abstractmethod
	def get_annotations_by_image_path(self, img_path: str) -> dict:
		pass


class FileNameSepParser(GalleryAnnotationsParser):
	"""
	Parser para obtener anotaciones a partir del nombre de las imágenes.
	El nombre del fichero es dividido con un separador y cada elemento obtenido es una anotación.
	Ejemplo:
		fp = FileNameSepParser(('label', 'age', 'sex'), sep='_')
		annots = fp('C:/dir/Fulano_32_M.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M' }
	"""

	def __init__(self, annot_names, sep='-'):
		self.annot_names = annot_names
		self.sep = sep

	def __call__(self, img_path: str) -> dict:
		return self.get_annotations_by_image_path(img_path)

	def get_annotations_by_image_path(self, img_path: str) -> dict:
		_, file = os.path.split(img_path)
		filename, _ = os.path.splitext(file)
		tokens = self._split_tokens(filename)
		annots = {}
		annots.keys()
		for i, token in enumerate(tokens):
			if i == len(self.annot_names):
				break
			annot_name = self.annot_names[i]
			annots[annot_name] = token
		return annots

	def _split_tokens(self, filename: str):
		if len(self.sep) == 1:
			return filename.split(sep=self.sep)
		else:
			tokens = []
			string = filename
			for separator in self.sep:
				token, string = string.split(separator, 1)
				tokens.append(token)
			return tokens


class FolderParser(GalleryAnnotationsParser):
	"""
	Parser para obtener anotaciones a partir del directorio de las imágenes.
	Las anotaciones se obtienen El nombre del fichero es dividido con un separador y cada elemento obtenido es una anotación.
	Ejemplo 1:
		fp = FolderParser((('label', 'age', 'sex'), sep='_'))
		annots = fp('C:/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M' }

	Ejemplo 2:
		fp = FolderParser([(('label', 'age', 'sex'), sep='_'), (('video')])
		annots = fp('C:/Video1/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M', 'video': 'Video1' }
	"""

	def __init__(self, annot_names, sep='-'):
		self.annot_names = annot_names
		self.sep = sep

	def __call__(self, img_path: str) -> dict:
		return self.get_annotations_by_image_path(img_path)

	def get_annotations_by_image_path(self, img_path: str) -> dict:
		_, file = os.path.split(img_path)
		filename, _ = os.path.splitext(file)
		tokens = filename.split(sep=self.sep)
		annots = {}
		annots.keys()
		for i, token in enumerate(tokens):
			if i == len(self.annot_names):
				break
			annot_name = self.annot_names[i]
			annots[annot_name] = token
		return annots