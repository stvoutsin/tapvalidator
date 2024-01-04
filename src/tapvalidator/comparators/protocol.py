from typing import Protocol

__all__ = ["Comparator"]


class Comparator(Protocol):
    """Protocol class for defining the methods / attributes of a class that implements a
    Comparison functionality"""

    @staticmethod
    def compare(actual, expected):
        """Compare two things"""
        ...
