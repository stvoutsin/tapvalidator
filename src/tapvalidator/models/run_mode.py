from enum import auto

__all__ = ["Mode"]


class Mode:
    """Enum for the various Run Modes for this package"""

    COMPARISON = auto()
    VALIDATION = auto()
    TABLE_VALIDATION_ONLY = auto()
