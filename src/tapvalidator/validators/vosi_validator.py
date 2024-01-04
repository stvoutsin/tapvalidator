from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import ValidationResult
from tapvalidator.models.status import Status


class VOSIValidator:
    """Validator for VOSI endpoints of a TAP Service
    VOSI endpoints is the /tables metadata endpoints of a TAP Service"""

    def __init__(self, tap_service: TAPService):
        self.tap_service = tap_service

    async def validate(self) -> ValidationResult:
        """Validate the VOSI Tables of a TAP Service

        Returns:
            bool: Whether the tap_service tables endpoint is valid
        """
        validation_result = ValidationResult()
        validation_result.status = Status.SUCCESS

        try:
            ElementTree.fromstring(self.tap_service.endpoints.tables)
        except ParseError:
            validation_result.status = Status.FAIL

        return validation_result
