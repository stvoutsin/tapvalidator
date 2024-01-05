import requests
from xml.etree.ElementTree import ParseError
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import VOSIValidationResult
from tapvalidator.models.status import Status
from tapvalidator.utility.xml_parser import XMLParser
from tapvalidator.utility.string_processor import StringProcessor
from tapvalidator.logger.logger import logger
from tapvalidator.validators.protocol import Validator
from tapvalidator.models.result import ValidationResult


class VOSIValidator(Validator):
    """Validator for VOSI endpoints of a TAP Service
    VOSI endpoints is the /tables metadata endpoints of a TAP Service"""

    def __init__(self, tap_service: TAPService):
        self.tap_service = tap_service

    async def validate(self) -> ValidationResult:
        """Validate the VOSI Tables of a TAP Service

        Returns:
            bool: Whether the tap_service tables endpoint is valid
        """
        validation_result = VOSIValidationResult()
        validation_result.status = Status.SUCCESS

        try:
            if self.tap_service.endpoints:
                response = requests.get(self.tap_service.endpoints.tables)
                if not XMLParser.check_element_exists(
                    StringProcessor.clean_text(response.text), "schema"
                ):
                    raise ValueError("Schema element does not exist in XML file")

        except (ParseError, ValueError) as exc:
            logger.error(exc)
            validation_result.messages.append(
                f"Unable to parse /tables endpoint. " f"Error was: {str(exc)}"
            )
            validation_result.status = Status.FAIL

        return validation_result
