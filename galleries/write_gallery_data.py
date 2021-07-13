import abc
from collections import Generator
import cv2 as cv
import logging
import os
from pathlib import Path
import pickle

from algorithms import IAlgorithm, IDescriptor, IDetector
from galleries.igallery import IGallery
from mnd_utils import files


class GalleryDataHandler:
	relative_data_dir = '_gallery_data'
	SEP = ' '
	EXT = '.pkl'

	def __init__(self, gallery: IGallery, write_data_dir):
		self.gallery = gallery
		self.write_data_dir = write_data_dir

	@abc.abstractmethod
	def _get_supported_algorithm_type(self) -> type:
		"""
		Tipo de algoritmo que este writer soporta para guardar/leer datos.
		:return:
		"""
		pass

	@abc.abstractmethod
	def _get_writer_folder_name(self) -> str:
		"""
		Nombre de la carpeta donde se guardarán los datos de este writer.
		:return:
		"""
		pass

	@abc.abstractmethod
	def _get_data(self, algorithm: IAlgorithm, gallery: IGallery):
		pass

	def get_root(self):
		return os.path.join(self.write_data_dir, self.relative_data_dir)

	def is_algorithm_valid(self, algorithm: IAlgorithm):
		return isinstance(algorithm, self._get_supported_algorithm_type())

	def _get_algorithm_folder(self, algorithm: IAlgorithm):
		"""
		Devuelve el directorio donde se guardan los datos de un algoritmo.
		:param algorithm: algoritmo del que se desean guardar los datos.
		:return:
		"""
		writer_folder = self._get_writer_folder_name()
		folder_dir = os.path.join(self.get_root(), writer_folder, algorithm.get_name())
		return folder_dir

	def _get_index_file_dir(self, algorithm: IAlgorithm):
		"""
		Devuelve la dirección del archivo donde se guardan, para cada posible configuración del algoritmo,
		la dirección del fichero donde se guardaron sus datos.
		:param algorithm: algoritmo del que se desean guardar los datos.
		:return:
		"""
		folder = self._get_algorithm_folder(algorithm)
		file_path = os.path.join(folder, 'index.txt')
		return file_path

	def _read_index_list(self, algorithm: IAlgorithm):
		"""
		Devuelve lista con los índices de datos guardados de un algoritmo.
		:param algorithm: algoritmo del que se desean guardar los datos.
		:return:
		"""
		indices = []
		index_file = self._get_index_file_dir(algorithm)
		if os.path.exists(index_file):
			with open(index_file) as file:
				for line in file:
					line = line.strip()
					index, algorithm_configuration = line.split(sep=self.SEP, maxsplit=1)
					index = int(index)
					indices.append((index, algorithm_configuration))
		return indices

	def _write_indices(self, algorithm: IAlgorithm, indices):
		"""
		Escribe el fichero de índices con los índices dados. Si el fichero no existe, se crea.
		Sobreescribe los índices que ya estuvieran guardados.
		:param algorithm:
		:param indices:
		:return:
		"""
		index_file = self._get_index_file_dir(algorithm)
		directory = Path(index_file).parent
		if not os.path.exists(directory):  # crear el directorio si no existe
			os.makedirs(directory)

		with open(index_file, 'w') as file:
			for index, conf in indices:
				file.write(f'{index}{self.SEP}{conf}\n')

	def _get_data_file_path(self, algorithm: IAlgorithm, indices) -> str:
		"""
		Devuelve la dirección del archivo donde se guardarán los datos de un algoritmo a partir de un índice.
		:param algorithm: algoritmo del que se desean guardar los datos.
		:return:
		"""
		data_file = None
		if len(indices) > 0:
			algorithm_folder = self._get_algorithm_folder(algorithm)
			algorithm_conf = algorithm.configuration_string()
			for index, conf in indices:
				if conf == algorithm_conf:
					data_file = os.path.join(algorithm_folder, f'{index}{self.EXT}')
					break
		return data_file

	def _add_algorithm_to_indices_if_not_exists(self, algorithm: IAlgorithm, indices: list) -> bool:
		algorithm_configuration = algorithm.configuration_string()
		exists = False
		max_index = -1
		for index, configuration in indices:
			if index > max_index:
				max_index = index
			if configuration == algorithm_configuration:
				exists = True
				break
		if not exists:
			indices.append((max_index + 1, algorithm_configuration))
		return not exists

	def _add_algorithm_to_index_file(self, algorithm: IAlgorithm):
		"""
		Añade un algoritmo al índice. Si el algoritmo existe ya, entonces no sucede nada.
		Si el fichero índice no está creado entonces se crea. Además devuelve la dirección del fichero donde se
		guardarán los datos del algoritmo.
		:param algorithm: algoritmo del que se desean guardar los datos.
		:return:
		"""
		indices = self._read_index_list(algorithm)
		added = self._add_algorithm_to_indices_if_not_exists(algorithm, indices)
		if added:
			self._write_indices(algorithm, indices)
		data_file = self._get_data_file_path(algorithm, indices)
		return data_file

	def _write_data(self, data: Generator, file_path: str):
		"""
		Guardar datos a partir de un generador.
		:param data:
		:param file_path:
		:return: devuelve True si se guardó, False si el archivo ya existía.
		"""
		if not os.path.exists(file_path):
			files.create_dir_of_file(file_path)
			file = open(file_path, 'wb')
			try:
				for d in data:
					pickle.dump(d, file)
					file.flush()
				file.close()
				return True
			except:
				file.close()
				raise RuntimeError('Un error ha ocurrido mientras se guardaban los datos.')

	def write_data(self, algorithm: IAlgorithm):
		if self.is_algorithm_valid(algorithm):
			indices = self._read_index_list(algorithm)
			self._add_algorithm_to_indices_if_not_exists(algorithm, indices)
			file_path = self._get_data_file_path(algorithm, indices)

			logging.info(f'Writing data with {algorithm} algorithm in {file_path}')

			data = self._get_data(algorithm, self.gallery)

			try:
				success = self._write_data(data, file_path)
				if success:
					self._write_indices(algorithm, indices)
			except:
				raise RuntimeError('Un error ha ocurrido mientras se guardaban los datos.')
		else:
			supported_type = self._get_supported_algorithm_type()
			msg = f'Tipo de dato incorrecto. El algoritmo debe ser de tipo {supported_type}.'
			logging.error(msg)
			raise TypeError(msg)

	def read_data(self, algorithm: IAlgorithm):
		"""
		Cargar datos guardados de un algoritmo.
		:param algorithm:
		:return:
		"""
		indices = self._read_index_list(algorithm)
		file_path = self._get_data_file_path(algorithm, indices)
		if file_path is not None and os.path.exists(file_path):
			file = open(file_path, "rb")
			end_reached = False
			while not end_reached:
				try:
					row_data = pickle.load(file)
					yield row_data
				except EOFError:
					end_reached = True
			file.close()
		else:
			raise IOError(f'No existen datos guardados para este algoritmo: {str(algorithm)}')

	def remove_corrupted_data(self):
		"""
		Eliminar datos guardados que estn corrompidos.
		:return:
		"""
		# TODO implementar esto
		pass

	def exists_data(self, algorithm: IAlgorithm):
		indices = self._read_index_list(algorithm)
		file_path = self._get_data_file_path(algorithm, indices)
		return file_path is not None and os.path.exists(file_path)

	def remove_data(self, algorithm: IAlgorithm):
		"""
		Eliminar algoritmo del índice así como sus datos.
		:param algorithm: algoritmo que se desea eliminar.
		:return:
		"""
		indices = self._read_index_list(algorithm)
		algorithm_conf = algorithm.configuration_string()
		exists = False
		for i, (index, conf) in enumerate(indices):
			if conf == algorithm_conf:
				exists = True
				break
		if exists:
			# eliminar los datos guardados
			data_file = self._get_data_file_path(algorithm, indices)
			if os.path.exists(data_file):
				os.remove(data_file)
			# quitar el algoritmo del índice
			indices.pop(i)
			self._write_indices(algorithm, indices)


class GalleryFeaturesDataHandler(GalleryDataHandler):

	def _get_supported_algorithm_type(self) -> type:
		return IDescriptor

	def _get_writer_folder_name(self) -> str:
		return 'features'

	def _get_data(self, algorithm: IAlgorithm, gallery: IGallery):
		if self.is_algorithm_valid(algorithm):
			for img_path in self.gallery.get_paths():
				img = cv.imread(img_path)
				feats = algorithm.features(img)
				yield img_path, feats


class GalleryDetectionsDataHandler(GalleryDataHandler):

	def _get_supported_algorithm_type(self) -> type:
		return IDetector

	def _get_writer_folder_name(self) -> str:
		return 'detections'

	def _get_data(self, algorithm: IAlgorithm, gallery: IGallery):
		if self.is_algorithm_valid(algorithm):
			for img_path in self.gallery.get_paths():
				img = cv.imread(img_path)
				dets = algorithm.detect(img)
				yield img_path, dets
