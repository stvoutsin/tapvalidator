import requests
from xml.etree.ElementTree import ParseError
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import ValidationResult
from tapvalidator.models.status import Status
from tapvalidator.utility.xml_parser import XMLParser
from tapvalidator.utility.string_processor import StringProcessor
from tapvalidator.logger.logger import logger
from tapvalidator.validators.protocol import Validator


class XMLValidator(Validator):
    """Generic XML Validator"""

    def __init__(self, tap_service: TAPService, expected_elements: list[str],
                 endpoint_name: str, ns: str = ""):
        self.tap_service = tap_service
        self.expected_elements = expected_elements
        self.endpoint_name = endpoint_name
        self.ns = ns

    async def validate(self) -> ValidationResult:
        """Validate that an XML endpoint contains the expected elements

        Returns:
            bool: Whether the XML endpoint contains the expected elements
        """
        validation_result = ValidationResult()
        validation_result.status = Status.SUCCESS

        try:
            if self.tap_service.endpoints:
                response = requests.get(self.tap_service.endpoints[self.endpoint_name])
                xml_str = StringProcessor.clean_text(response.text)
                for element in self.expected_elements:
                    if not XMLParser.check_element_exists(xml_string=xml_str,
                                                          element=element,
                                                          ns=self.ns):
                        raise ValueError(f"{element} element does not exist in XML "
                                         f"file")

        except (ParseError, ValueError) as exc:
            logger.error(exc)
            validation_result.messages.append(
                f"Unable to parse /{self.endpoint_name} endpoint. " f"Error was:"
                f" {str(exc)}"
            )
            validation_result.status = Status.FAIL

        return validation_result
