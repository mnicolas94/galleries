import random
from typing import Dict, Optional, Any, List

import numpy as np

from galleries.annotations_filtering.filter import FilterStatement
from galleries.igallery import IGallery


class TestGallery(IGallery):

    def __init__(self, name="Test", cant_images=1000000):
        self._name = name
        self._cant_images = cant_images

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_indices(self, filters: List[List[FilterStatement]] = None):
        yield from (x for x in range(self._cant_images))

    def get_annotations_by_index(self, img_index) -> dict:
        return {}

    def get_image_by_index(self, index: Any) -> np.ndarray:
        r = random.Random(index)
        random_number = r.randint(0, 255)
        return np.zeros((8, 8, 3), dtype=np.uint8) + random_number

    def get_annotations_types(self) -> Optional[Dict[str, type]]:
        return None

    def get_discrete_annotations_values(self) -> Dict[str, list]:
        return {}
