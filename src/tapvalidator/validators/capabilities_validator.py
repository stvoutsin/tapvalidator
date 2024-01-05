from tapvalidator.models.tap_service import TAPService
from tapvalidator.validators.xml_validator import XMLValidator


class CapabilitiesValidator(XMLValidator):
    """Validator for Availability endpoint of a TAP Service"""

    def __init__(self, tap_service: TAPService):
        super().__init__(
            tap_service=tap_service,
            expected_elements=["capability"],
            endpoint_name="capabilities",
        )
