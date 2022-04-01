from typing import Any

from galleries.annotations_filtering import ComparisonType


class FilterStatement:

    def __init__(self, annotation_key: str, comparison_type: ComparisonType, value: Any, is_negated: bool):
        self._annotation_key = annotation_key
        self._comparison_type = comparison_type
        self._value = value
        self._is_negated = is_negated

    def __iter__(self):
        return iter([self._annotation_key, self._comparison_type, self._value, self._is_negated])


if __name__ == '__main__':
    f = FilterStatement('asd', ComparisonType.EQUAL, 1, True)
    (a, b, c, d) = f
    print(a, b, c, d)
