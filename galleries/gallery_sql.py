import abc
import sqlite3
from sqlite3 import Connection
from typing import Dict, Optional, Any, List

import numpy as np
from propsettings.configurable import register_as_setting
from propsettings.setting_types.path_setting_type import Path

from galleries.annotations_filtering.filter import FilterStatement
from galleries.igallery import IGallery


class GallerySqlConnector:

    @abc.abstractmethod
    def connect(self):
        pass


class SqliteConnector(GallerySqlConnector):

    def __init__(self, database_path: str = ""):
        self._database_path = database_path

    def connect(self):
        return sqlite3.connect(self._database_path)

register_as_setting(SqliteConnector, "_database_path", setting_type=Path(False, []))


class SqlDataRetriever:

    @abc.abstractmethod
    def get_indices(self, cursor, filters: List[List[FilterStatement]] = None):
        pass

    @abc.abstractmethod
    def get_annotations_by_index(self, cursor, index: Any) -> dict:
        pass

    @abc.abstractmethod
    def get_image_by_index(self, cursor, index: Any) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_annotations_types(self, cursor) -> Optional[Dict[str, type]]:
        pass

    @abc.abstractmethod
    def get_discrete_annotations_values(self, cursor) -> Dict[str, list]:
        pass


class GallerySql(IGallery):

    def __init__(
            self,
            name: str = "",
            connector: GallerySqlConnector = SqliteConnector(),
            data_retriever: SqlDataRetriever = None
    ):
        self._name = name
        self._connector = connector
        self._data_retriever = data_retriever
        self._connection: Optional[Connection] = None

    def __getstate__(self):
        state = self.__dict__
        state.pop("_connection")  # do not serialize connection because it is not serializable
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self._connection = None

    @property
    def _get_connection(self):
        if not self._is_connected():
            self._connect()
        return self._connection

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_indices(self, filters: List[List[FilterStatement]] = None):
        cur = self._get_connection.cursor()
        return self._data_retriever.get_indices(cur, filters)

    def get_annotations_by_index(self, index: Any) -> dict:
        cur = self._get_connection.cursor()
        return self._data_retriever.get_annotations_by_index(cur, index)

    def get_image_by_index(self, index: Any) -> np.ndarray:
        cur = self._get_connection.cursor()
        return self._data_retriever.get_image_by_index(cur, index)

    def get_annotations_types(self) -> Optional[Dict[str, type]]:
        cur = self._get_connection.cursor()
        return self._data_retriever.get_annotations_types(cur)

    def get_discrete_annotations_values(self) -> Dict[str, list]:
        cur = self._get_connection.cursor()
        return self._data_retriever.get_discrete_annotations_values(cur)

    def _is_connected(self):
        return self._connection is not None

    def _connect(self):
        if self._is_connected():
            self._disconnect()
        self._connection = self._connector.connect()

    def _disconnect(self):
        self._connection.close()
        self._connection = None


