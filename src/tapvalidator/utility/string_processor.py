from tapvalidator.constants.reserved_keywords import RESERVED_KEYWORDS
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import ValidationResult

__all__ = ["StringProcessor"]


class StringProcessor:
    @staticmethod
    def fix_keywords(string: str) -> str:
        """
        Add quotes around keywords in a query
        Args:
            string (str): The query

        Returns:
            str: The updated query
        """
        if string.upper() in RESERVED_KEYWORDS:
            return f'"{string}"'
        else:
            return string

    @staticmethod
    def generate_alert_message(
        validation_result: ValidationResult, tap_service: TAPService
    ) -> str:
        """Generate the content of an alert message for a failed query
        Args:
            validation_result (ValidationResult): The validation result
        Returns:
            str: The updated query
        """
        res = f"Notification for tap_service: [{tap_service}]\n"
        res += validation_result.as_string()
        return res

    @staticmethod
    def clean_text(string: str) -> str:
        """Clean the string from \n and \t chars
        Args:
            string (str): The string
        Returns:
            str: The updated string
        """
        return string.replace("\n", "").replace("\t", "")
