from enum import Enum


class Status(Enum):
    """Enum for the various Status types for a Query or Validation check"""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    TRUNCATED = "TRUNCATED"
    PENDING = "PENDING"
    COLUMN_VALIDATION_FAIL = "COLUMN_VALIDATION_FAIL"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
