import abc
import numpy as np
from typing import List, Any, Dict, Optional

from galleries.annotations_filtering.filter import FilterStatement


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
    def get_annotations_types(self) -> Optional[Dict[str, type]]:
        pass

    @abc.abstractmethod
    def get_discrete_annotations_values(self) -> Dict[str, list]:
        pass