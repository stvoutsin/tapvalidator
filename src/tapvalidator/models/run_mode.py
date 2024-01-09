from enum import Enum

__all__ = ["Mode"]


class Mode(Enum):
    """Enum for the various Run Modes for this package"""

    COMPARISON = "COMPARISON"
    VALIDATION = "VALIDATION"
    TABLE_VALIDATION = "TABLE_VALIDATION"
