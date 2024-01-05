from typing import Protocol
from tapvalidator.models.result import ValidationResult


class Validator(Protocol):
    """Validator Protocol definition"""

    async def validate(self) -> ValidationResult:
        ...
